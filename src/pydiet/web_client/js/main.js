// Javascript code entry point
// Copyright 2024-2026 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT
import {setup_health} from "./health"
import {get_instruments} from "./instrument"
import {setup_instrument_settings, setup_theme_settings} from "./settings";

// Set up server health monitoring
setup_health()

// Set up theme section of settings
setup_theme_settings();

get_instruments().then( (instruments) => {
// Set up instrument section of settings
	setup_instrument_settings(instruments);
});


