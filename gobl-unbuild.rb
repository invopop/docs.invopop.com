#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require 'tempfile'
require 'open3'
require 'optparse'

# Script to minimize a GOBL file by removing all calculated fields.
# Usage: ruby minimize.rb [-i] <input_file>
#
# The script works by:
# 1. Building the input file with `gobl build` to get a fully calculated version
# 2. Extracting the digest and doc content
# 3. Iteratively testing each field by removing it and rebuilding
# 4. Keeping only fields that are required to reproduce the same digest
class GOBLMinimizer
  def initialize(input_file, in_place: false)
    @input_file = input_file
    @in_place = in_place
    @gobl_binary = '/Users/markmackay/go/bin/gobl'
    @target_digest = nil
    @original_doc = nil
    @input_doc = nil
    @indent_style = nil
  end

  def run
    # Step 1: Read the input document to preserve special fields
    begin
      @input_doc = JSON.parse(File.read(@input_file))
    rescue JSON::ParserError => e
      STDERR.puts "Error parsing input file: #{e.message}"
      exit 1
    end

    # Step 2: Detect indentation style from input file
    detect_indent_style

    # Step 3: Build the input file to get the fully calculated version
    built_envelope = build_file(@input_file)
    unless built_envelope
      STDERR.puts "Error: Failed to build input file"
      exit 1
    end

    # Step 4: Extract digest and doc
    @target_digest = built_envelope.dig('head', 'dig', 'val')
    @original_doc = built_envelope['doc']

    unless @target_digest && @original_doc
      STDERR.puts "Error: Could not extract digest or doc from built envelope"
      exit 1
    end

    STDERR.puts "Target digest: #{@target_digest}"
    STDERR.puts "Indentation: #{@indent_style[:type]} (#{@indent_style[:size]} #{@indent_style[:type] == :tab ? 'tab' : 'spaces'})"
    STDERR.puts "Starting minimization process..."

    # Step 5: Minimize the doc by testing each field
    minimized_doc = minimize_structure(@original_doc, [])

    # Step 6: Remove all uuid fields (they are calculated but random)
    STDERR.puts "Removing all uuid fields..."
    minimized_doc = remove_uuid_fields(minimized_doc)

    # Step 7: Restore preserved fields from input that don't appear in built doc
    STDERR.puts "Restoring preserved fields from input..."
    minimized_doc = restore_input_fields(minimized_doc)

    # Step 8: Output the minimized doc
    output = format_json(minimized_doc)

    if @in_place
      File.write(@input_file, output)
      STDERR.puts "File updated in place: #{@input_file}"
    else
      puts output
    end
  end

  private

  # Build a GOBL file and return the resulting envelope as a hash
  def build_file(file_path)
    stdout, stderr, status = Open3.capture3(@gobl_binary, 'build', '-e', file_path)

    if status.success?
      begin
        JSON.parse(stdout)
      rescue JSON::ParserError => e
        STDERR.puts "Error parsing GOBL build output: #{e.message}"
        nil
      end
    else
      STDERR.puts "Error building file: #{stderr}"
      nil
    end
  end

  # Build a doc (not an envelope) by writing it to a temp file and running gobl build
  def build_doc(doc)
    Tempfile.create(['gobl_doc', '.json']) do |f|
      f.write(JSON.generate(doc))
      f.flush
      build_file(f.path)
    end
  end

  # Check if a doc produces the same digest as the target
  def same_digest?(doc)
    envelope = build_doc(doc)
    return false unless envelope

    digest = envelope.dig('head', 'dig', 'val')
    digest == @target_digest
  end

  # Get a value from a nested structure using a path (array of keys/indices)
  def get_at_path(obj, path)
    path.reduce(obj) { |acc, key| acc[key] }
  end

  # Set a value in a nested structure using a path (array of keys/indices)
  def set_at_path(obj, path, value)
    if path.empty?
      return value
    end

    obj = deep_dup(obj)
    current = obj
    path[0...-1].each do |key|
      current = current[key]
    end
    current[path[-1]] = value
    obj
  end

  # Delete a key/index from a nested structure using a path
  def delete_at_path(obj, path)
    return nil if path.empty?

    obj = deep_dup(obj)
    current = obj
    path[0...-1].each do |key|
      current = current[key]
    end

    if current.is_a?(Hash)
      current.delete(path[-1])
    elsif current.is_a?(Array)
      current.delete_at(path[-1])
    end

    obj
  end

  # Minimize a structure recursively by testing each field/element
  # path is an array representing the current location in the structure
  def minimize_structure(current_doc, path)
    current_value = get_at_path(@original_doc, path)

    case current_value
    when Hash
      minimize_hash_at_path(current_doc, path)
    when Array
      minimize_array_at_path(current_doc, path)
    else
      current_doc
    end
  end

  # Order hash keys according to precedence rules:
  # 1. 'ext' fields first
  # 2. Other fields in the middle
  # 3. 'key' fields last
  def order_keys(keys)
    ext_keys = []
    key_keys = []
    other_keys = []

    keys.each do |k|
      if k == 'ext'
        ext_keys << k
      elsif k == 'key'
        key_keys << k
      else
        other_keys << k
      end
    end

    ext_keys + other_keys + key_keys
  end

  # Fields that should never be removed, even if they don't affect the digest
  PRESERVED_FIELDS = ['$regime', '$addons'].freeze

  # Check if a field should be preserved (never removed)
  def preserve_field?(field_path)
    # Preserve fields at the root level only
    return false unless field_path.length == 1
    PRESERVED_FIELDS.include?(field_path[0])
  end

  # Minimize a hash at a specific path in the document
  def minimize_hash_at_path(current_doc, path)
    hash_value = get_at_path(current_doc, path)
    keys = order_keys(hash_value.keys)
    result_doc = current_doc

    keys.each do |key|
      field_path = path + [key]
      path_string = field_path.join(' > ')
      STDERR.puts "Testing field: #{path_string}"

      # Check if this field should be preserved
      if preserve_field?(field_path)
        STDERR.puts "  → Field '#{path_string}' is preserved (kept)"
        # Keep the field but minimize its value recursively
        result_doc = minimize_structure(result_doc, field_path)
        next
      end

      # Try to remove this field
      test_doc = delete_at_path(result_doc, field_path)

      if same_digest?(test_doc)
        STDERR.puts "  → Field '#{path_string}' is optional (removed)"
        result_doc = test_doc
      else
        STDERR.puts "  → Field '#{path_string}' is required (kept)"
        # Keep the field but minimize its value recursively
        result_doc = minimize_structure(result_doc, field_path)
      end
    end

    result_doc
  end

  # Minimize an array at a specific path in the document
  def minimize_array_at_path(current_doc, path)
    array_value = get_at_path(current_doc, path)
    result_doc = current_doc

    # Process array elements in reverse order to avoid index shifting issues
    (array_value.length - 1).downto(0) do |index|
      element_path = path + [index]
      path_string = element_path.join(' > ')
      STDERR.puts "Testing array element: #{path_string}"

      # Try to remove this element
      test_doc = delete_at_path(result_doc, element_path)

      if same_digest?(test_doc)
        STDERR.puts "  → Element '#{path_string}' is optional (removed)"
        result_doc = test_doc
      else
        STDERR.puts "  → Element '#{path_string}' is required (kept)"
        # Keep the element but minimize it recursively
        result_doc = minimize_structure(result_doc, element_path)
      end
    end

    result_doc
  end

  # Deep duplicate a value
  def deep_dup(value)
    case value
    when Hash
      value.transform_values { |v| deep_dup(v) }
    when Array
      value.map { |v| deep_dup(v) }
    else
      value.duplicable? ? value.dup : value
    end
  end

  # Remove all 'uuid' fields from the document recursively
  def remove_uuid_fields(value)
    case value
    when Hash
      result = {}
      value.each do |k, v|
        # Skip uuid fields
        next if k == 'uuid'
        # Recursively process the value
        result[k] = remove_uuid_fields(v)
      end
      result
    when Array
      value.map { |v| remove_uuid_fields(v) }
    else
      value
    end
  end

  # Restore preserved fields from the input document that don't appear in built doc
  # Also ensures proper field ordering with $ fields at the top
  def restore_input_fields(minimized_doc)
    result = {}
    
    # First, add $ fields in order: $schema, $regime, $addons, $tags
    result['$schema'] = minimized_doc['$schema'] if minimized_doc['$schema']
    result['$regime'] = minimized_doc['$regime'] if minimized_doc['$regime']
    result['$addons'] = @input_doc['$addons'] if @input_doc['$addons']
    result['$tags'] = minimized_doc['$tags'] if minimized_doc['$tags']
    
    # Then add all other fields
    minimized_doc.each do |key, value|
      next if key.start_with?('$')
      result[key] = value
    end
    
    result
  end

  # Detect indentation style from the input file
  def detect_indent_style
    content = File.read(@input_file)
    lines = content.lines

    # Look for the first indented line
    lines.each do |line|
      # Check for tab indentation
      if line.start_with?("\t")
        @indent_style = { type: :tab, size: 1 }
        return
      end

      # Check for space indentation
      if line =~ /^( +)\S/
        spaces = $1.length
        @indent_style = { type: :space, size: spaces }
        return
      end
    end

    # Default to 2 spaces if nothing detected
    @indent_style = { type: :space, size: 2 }
  end

  # Format JSON with the detected indentation style
  def format_json(obj)
    if @indent_style[:type] == :tab
      # JSON.pretty_generate doesn't support tabs directly, so we need to convert
      json = JSON.pretty_generate(obj, indent: ' ' * @indent_style[:size])
      # Replace leading spaces with tabs
      json.gsub(/^( +)/) { |match| "\t" * (match.length / @indent_style[:size]) }
    else
      JSON.pretty_generate(obj, indent: ' ' * @indent_style[:size])
    end
  end
end

# Check if value supports dup
class Object
  def duplicable?
    true
  end
end

class NilClass
  def duplicable?
    false
  end
end

class FalseClass
  def duplicable?
    false
  end
end

class TrueClass
  def duplicable?
    false
  end
end

class Symbol
  def duplicable?
    false
  end
end

class Numeric
  def duplicable?
    false
  end
end

# Main execution
options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: minimize.rb [options] <input_file>"

  opts.on("-i", "--in-place", "Modify the input file in place") do
    options[:in_place] = true
  end

  opts.on("-h", "--help", "Show this help message") do
    puts opts
    exit
  end
end.parse!

if ARGV.empty?
  STDERR.puts "Usage: ruby minimize.rb [-i] <input_file>"
  STDERR.puts "  -i, --in-place    Modify the input file in place"
  exit 1
end

input_file = ARGV[0]

unless File.exist?(input_file)
  STDERR.puts "Error: File not found: #{input_file}"
  exit 1
end

minimizer = GOBLMinimizer.new(input_file, in_place: options[:in_place])
minimizer.run