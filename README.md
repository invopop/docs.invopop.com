# Invopop Documentation

The content and configuration powering the documentation available at [docs.invopop.com](https://docs.invopop.com)

### 👩‍💻 Development

Install the [Mintlify CLI](https://www.npmjs.com/package/mintlify) to preview the documentation changes locally. To install, use the following command:

```
npm i -g mint
```

Run the following command at the root of your documentation (where `docs.json` is)

```
mint dev
```

### 🔨 Building Invoice Examples

The project includes a script to automatically build invoice examples from minimal JSON files using the GOBL CLI tool.

The `build-min-files.sh` script:
- Finds all `.min.mdx` files in the `/snippets` directory
- Extracts JSON from each MDX file's code block
- Builds the JSON using `gobl build` to calculate totals, add UUIDs, and validate
- Outputs the built JSON to corresponding `.mdx` files (without the `.min` suffix)
- Preserves the original code block title
- Handles errors gracefully and continues processing other files

To use the script:

```bash
./build-min-files.sh
```

The script will:
- Process all `.min.mdx` files in the snippets directory
- Overwrite existing `.mdx` files if they exist
- Report any build errors and continue processing
- Display a summary of processed files and errors at the end

**Prerequisites:** The script requires the `gobl` CLI tool to be installed and available in your PATH.

### 🪄 Tips & Tricks

If your local preview is out of sync with what you see on the web in the production version, update your local CLI:

```
mint update
```

The CLI can assist with validating reference links made in your documentation. To identify any broken links, use the following command:

```
mint broken-links
```

You can rename and update all references to files using the following command:

```
mint rename <oldFilename> <newFilename>
```

You can use the CLI to check your OpenAPI file for errors using the following command:

```
mint openapi-check <openapiFilenameOrUrl>
```