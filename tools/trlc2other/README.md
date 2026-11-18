# trlc2other

The scripts ```make_docx.[bat|sh]``` will generate a docx file from the requirements and architecture to the ```./out/``` folder.

The scripts ```make_reqif.[bat|sh]``` will generate ReqIF files from the requirements, architecture and test cases to the ```./out/``` folder.

Both use the project converters in [../converter](../converter). The reStructuredText and Markdown
documentation is built by trlcdoc, see [Tools](../README.md).

PlantUML is taken from the `PLANTUML` environment variable (path to plantuml.jar or a server URL).
If it is not set, the scripts call `trlcdoc plantuml`, which downloads the jar into `build/trlcdoc/plantuml`.
