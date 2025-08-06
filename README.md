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