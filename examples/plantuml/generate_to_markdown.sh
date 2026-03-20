#!/bin/bash

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
# Copyright (c) 2024 - 2026 NewTec GmbH
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

OUT_PATH=./out

# Use either local jar file or plantuml server URL for rendering.
export PLANTUML=plantuml.jar
#export PLANTUML=http://www.plantuml.com/plantuml

# check if given parameter is not a URL
if ! [[ $PLANTUML =~ ^https?:// ]]
then
    # Assume local plantuml jar usage, download if not available.
    if [ ! -f "$PLANTUML" ]
    then
        echo "Download PlantUML java program..."
        wget https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar -O $PLANTUML
    fi
fi

pyTRLCConverter --source=. --out=$OUT_PATH --project=req.py markdown

if [ $? -ne 0 ]; then
    read -p "Press any key to continue..."
fi
