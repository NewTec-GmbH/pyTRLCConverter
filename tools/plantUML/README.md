# PlantUML

The scripts ```get_plantuml.[bat|sh]``` download the PlantUML java JAR file to this folder and set the environment variable ```PLANTUML``` to the absolute path to it.

## Environment Variables

| Environment Variable  | Description                                                                                                                                                     | Default |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `PLANTUML`            | Path to `plantuml.jar` or URL of a PlantUML server.                                                                                                             | -       |
| `PLANTUML_VERIFY_SSL` | Set to `false` to disable SSL certificate verification for PlantUML server requests. Useful for internal servers with self-signed or corporate CA certificates. | `true`  |
