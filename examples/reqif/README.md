# pyTRLCConverter <!-- omit in toc -->

## Simple Requirement with ReqIf Example

The example demonstrates how the requirements in a **single file** are converted to ReqIF format **without any project specific conversion**, but **with a translation file** to translate the requirement type attribute name and with **render configuration**. The pyTRLCConverter will generate a simple output without project-specific conversion functions.

## Analyze ReqIF File

Analyze an existing ReqIF file (.reqif or .reqifz) by replacing &lt;INPUT&gt; with the ReqIF file path.

If no output option is used, the report will be written to the same location as the ReqIF file.

```bash
python -o ./out/analysis.md ./reqif_list_types/reqif_list_types.py <INPUT>
```

It will create an ```./out/analyzis.md``` file that shows all kind of ReqIF specific types.

## Validate Generated ReqIF File

Validate a ReqIF file (.reqif or .reqifz) against ReqIF format compliance, XHTML compliance and against ReqIF implementation guide.

Replace &lt;INPUT&gt; with the ReqIF file path.

```bash
python ./validate_reqif/validate_reqif.py <INPUT>
```

If no output option is used, the files will be written to the same location as the ReqIF file.

## Prepare pyTRLCConverter Inputs from ReqIF File

Prepare .trlc, .rsl, render configuration and translation from a given ReqIF file (.reqif or .reqifz).

Replace &lt;INPUT&gt; with the ReqIF file path.

```bash
python ./reqif_to_rsl/reqif_to_rsl.py -o out_reqif_to_rsl -p Req <INPUT>
```

## Issues, Ideas And Bugs

If you have further ideas or you found some bugs, great! Create a [issue](https://github.com/NewTec-GmbH/pyTRLCConverter/issues) or if you are able and willing to fix it by yourself, clone the repository and create a pull request.

## License

The whole source code is published under [GPL-3.0](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE).
Consider the different licenses of the used third party libraries too!

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as above, without any additional terms or conditions.
