# pyTRLCConverter <!-- omit in toc -->

## Examples

The following examples show different functionality as well as possibilities. Because one part of the innovation is still on the user side, e.g. by introducing a Diagram type and not just deal with requirements.

| Example                                                       | Single/Multiple source(s) | With project specific conversion functions | Diagram support | Single output document | Translation | Render Configuration |
| ------------------------------------------------------------- | ------------------------- | ------------------------------------------ | --------------- | ---------------------- | ----------- | -------------------- |
| [plantuml](./plantuml/)                                       | Single                    | Yes                                        | Yes             | No                     | No          | No                   |
| [Convert to ReqIF format](./reqif/)                           | Single                    | No                                         | No              | No                     | Yes         | Yes                  |
| [simple_req](./simple_req/)                                   | Single                    | No                                         | No              | No                     | No          | No                   |
| [simple_req_multi](./simple_req_multi/)                       | Multiple                  | No                                         | No              | No                     | No          | No                   |
| [simple_req_multi_single_out](./simple_req_multi_single_out/) | Multiple                  | No                                         | No              | Yes                    | No          | No                   |
| [simple_req_proj_spec](./simple_req/)                         | Single                    | Yes                                        | No              | No                     | No          | No                   |
| [simple_req_translation](./simple_req_translation/)           | Single                    | No                                         | No              | No                     | Yes         | No                   |

Also look into the [tools/ProjectConverter](../tools/ProjectConverter) folder, which contains more sophisticated converter implementations. These are the converters for the pyTRLCConverter model files in [trlc/model](../trlc/model/).

## Issues, Ideas And Bugs

If you have further ideas or you found some bugs, great! Create a [issue](https://github.com/NewTec-GmbH/pyTRLCConverter/issues) or if you are able and willing to fix it by yourself, clone the repository and create a pull request.

## License

The whole source code is published under [GPL-3.0](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE).
Consider the different licenses of the used third party libraries too!

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as above, without any additional terms or conditions.
