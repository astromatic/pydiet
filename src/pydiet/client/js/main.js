// Javascript code entry point
// Copyright CEA/CFHT/CNRS/UParisSaclay
// Licensed under MIT
import {prefersdark, toggle_dark_theme} from "./theme";
import * as settings from "./settings";

// Set theme to dark if this is the users preference
toggle_dark_theme(prefersdark.matches);

