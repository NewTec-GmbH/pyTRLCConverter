#!/bin/bash

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
# Copyright (c) 2024 - 2025 NewTec GmbH
#
# This file is part of pyTRLCConverter program.
#
# The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# The pyTRLCConverter program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyTRLCConverter.
# If not, see <https://www.gnu.org/licenses/>.

# ********** Argument validation **********
# Enable online report generation only if "online" argument is provided.
# If no argument is provided, only local file paths are used.
# If any other argument is provided, an error is raised.
ONLINE_REPORT_OPTION=''
if [ "$#" -gt 1 ]; then
    echo "Error: Too many arguments. Only optional 'online' is allowed." >&2
    exit 1
elif [ "$#" -eq 1 ]; then
    if [ "$1" == "online" ]; then
        ONLINE_REPORT_OPTION="online"
    else
        echo "Error: Invalid argument '$1'. Only optional 'online' is allowed." >&2
        exit 1
    fi
fi

# Create reStructured Text documentation from TRLC models and files.
(cd trlc2other; ./make_rst.sh)

# Create unit test reports
(cd testReport; ./make_rst.sh)

# Create tracing report from TRLC and source files.
(cd traceReport; ./make.sh $ONLINE_REPORT_OPTION)

#Create HTML documentation.
(cd plantUML; . ./get_plantuml.sh; cd ..;cd deployDoc; make html)
