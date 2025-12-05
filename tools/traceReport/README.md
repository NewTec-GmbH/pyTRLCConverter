# traceReport

## Overview

The overview shows in general which tools are involved to generate tracing reports.

![tracing_toolchain](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/NewTec-GmbH/pyTRLCConverter/refs/heads/main/tools/traceReport/tracing_toolchain.puml)

The shown tool call chains are hidden in the script:

* ```make.[bat|sh]```

## How to generate a local tracing report?

The following tracing report will consider the local checked out files!

1. Call make.[bat|sh] depended on your OS.
2. It will create the tracability report in the ```./out``` folder.
3. Open ```sw_req_tracing_online_report.html``` and ```sw_test_tracing_online_report.html``` in your browser.

Note that the file name still contains the \_online\_ part to allow tool interoperability.

## How to generate a online tracing report?

The following tracing report will consider the files on git SHA base for unique identification.

 A call to make.[bat|sh] with the "online" argument will try to build the report in the online mode.
 This depends on several environemt variables (like %BASE_URL" and %COMMIT_ID%) and is supposed to be run in the Continuous Integration environment.
