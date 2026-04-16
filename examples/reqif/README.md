# pyTRLCConverter <!-- omit in toc -->

## ReqIF Example

The ReqIF format is written for classical requirements tools in mind that were table oriented. The art of conversion is now how to transform TRLC sections and records to ReqIF format, that can be imported by other requirements tools.

### Overview

- A TRLC file contains the requirements of one document.
- ReqIF format doens't support links between documents. Unfortunately every requirements tool handles this tool specific. The workaround in TRLC is to use the single document mode to overcome this problem.
- A TRLC file always requires a document section, which is the first section in the file without any preceeding requirements.
- A requirement hierarchy is modelled by using TRLC sections. The preceeding requirement is the parent of all the children in the section.
- ReqIF has XHTML support that is supported by pyTRLCConverter too.
  - Option 1: Write in plain text.
  - Option 2: Write in Markdown or GitHub Flavored Markown. This will be converted to XHTML, which is recommended.
  - Option 3: Write in XHTML if full XHTML support is required.
- The [ReqIF implementation guide](https://www.prostep.org/fileadmin/prod-download/ProSTEP_iViP_ImplementationGuide_ReqIF_V1-10_aw.pdf) explains which system attributes are required for requirements exchange with other requirements tools.

### Problems And Solutions

#### TRLC Attribute To ReqIF System Attribute Mapping

TRLC attributes are mapped by translation, that means a translation JSON file is required. If you think why using a translation instead of changing the attribute name itself, it won't work. Thats because e.g. the dot (".") is a special character and can't be used for TRLC attribute names. On the other hand the ReqIF implementation guideline denys the system attribute prefix for attribute names, its only used for export/import.

Example:

```plain
type MyReqType {
    summary     String
    description String
}
```

The MyReqType::description is mapped to ReqIF.Text by

```json
{
    "MyReqType": {
        "summary": "ReqIF.Name",
        "description": "ReqIF.Text"
    }
}
```

Notes:

- ```ReqIF.Name``` is e.g. the short object text in IBM DOORS, according to ReqIF implementation guideline.
- ```ReqIF.Text``` is e.g. the object text in IBM DOORS, according to ReqIF implementation guideline.

#### Choose The Right Format

To specify which attribute will be written e.g. in Markdown etc., a render configuration is required.

Example for writing MyReqType::description in GitHub Flavored Markdown:

```json
{
    "renderCfg": 
    [
        {
            "package": ".*",
            "type": "MyReqType",
            "attribute": "description",
            "format": "gfm"
        }
    ]   
}
```

#### Style GFM Tables

When an attribute is rendered in GitHub Flavored Markdown (`"format": "gfm"`), tables contained in that attribute are converted to XHTML. You can control the visual style of those tables by adding the optional `tableOptions` key to the render configuration item.

| Key            | Description                                                    | Example value                                           |
| -------------- | -------------------------------------------------------------- | ------------------------------------------------------- |
| `border`       | CSS style applied to the `<table>` element's `style` attribute | `"border: 1px solid black; border-collapse: collapse;"` |
| `headingStyle` | CSS style applied to every `<th>` cell's `style` attribute     | `"background-color: #c0c0c0;"`                          |

Both keys are optional. If `tableOptions` is omitted entirely, no inline style is added to the generated table elements.

Example — render `MyReqType::description` as GFM with a bordered table and a grey header row:

```json
{
    "renderCfg": [
        {
            "package": ".*",
            "type": "MyReqType",
            "attribute": "description",
            "format": "gfm",
            "tableOptions": {
                "border": "border: 1px solid black; border-collapse: collapse;",
                "headingStyle": "background-color: #c0c0c0;"
            }
        }
    ]
}
```

#### Attach External Files

TRLC doesn't know out of the box how to deal with attachments, images and etc. Therefore the render configuration provides the format "path". It is assumed that the attribute value contains the path to related artifcat. It will be provided in the ReqIF format as XHTML and the artifact will be part of the reqifz file.

Example:

```json
{
    "renderCfg": 
    [
        {
            "package": ".*",
            "type": "Image",
            "attribute": "file_path",
            "format": "path"
        }
    ]   
}
```

## Supporting Tools

### Analyze ReqIF File

Analyze an existing ReqIF file (.reqif or .reqifz) by replacing &lt;INPUT&gt; with the ReqIF file path.

If no output option is used, the report will be written to the same location as the ReqIF file.

```bash
python -o ./out/analysis.md ./reqif_list_types/reqif_list_types.py <INPUT>
```

It will create an ```./out/analyzis.md``` file that shows all kind of ReqIF specific types.

### Validate Generated ReqIF File

Validate a ReqIF file (.reqif or .reqifz) against ReqIF format compliance, XHTML compliance and against ReqIF implementation guide.

Replace &lt;INPUT&gt; with the ReqIF file path.

```bash
python ./validate_reqif/validate_reqif.py <INPUT>
```

If no output option is used, the files will be written to the same location as the ReqIF file.

### Prepare pyTRLCConverter Inputs from ReqIF File

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
