import * as React from 'react';
import DashboardTitle from '../dashboard/DashboardTitle';
import { Flex } from '@hddcoin/core';
import { Grid, Link } from '@material-ui/core';
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import 'xterm/css/xterm.css';
import c from "ansi-colors";
import path from 'path';
import { existsSync, readFileSync } from 'fs';
import { Trans } from '@lingui/macro';

const electron = require('electron');
const clipboard = electron.clipboard;
const pty = require('node-pty');
							
const PY_MAC_DIST_FOLDER = '../../../app.asar.unpacked/daemon';
const PY_WIN_DIST_FOLDER = '../../../app.asar.unpacked/daemon';
const fullPath = (existsSync((process.platform === 'win32') ? path.join(__dirname, PY_WIN_DIST_FOLDER) : path.join(__dirname, PY_MAC_DIST_FOLDER))) ? ((process.platform === 'win32') ? path.join(__dirname, PY_WIN_DIST_FOLDER) : path.join(__dirname, PY_MAC_DIST_FOLDER)) : path.join(__dirname, '../../../venv/bin');
const ENV_HDDCOIN = ((process.platform === 'win32') ? '$env:Path += ";' : 'export PATH="$PATH:') + fullPath + '"';
const SHELL = (process.platform === 'win32') ? 'powershell.exe' : 'bash';

const term = new Terminal({
  convertEol: true,
  fontFamily: `'Fira Mono', monospace`,
});

const fitAddon = new FitAddon();

const ptyProcess = pty.spawn(SHELL, [], {
  name: 'xterm-color',
  cwd: fullPath,
  env: process.env
});

// Set path enviroment
ptyProcess.write(ENV_HDDCOIN + '\r\n');
ptyProcess.write('cd $home \r\n');
ptyProcess.write('clear \r');
ptyProcess.write('hddcoin -h\r');

// Write data from ptyProcess to terminal
ptyProcess.on('data', function(data) {
  term.write(data);
});

// Get keys
term.onKey(key => {
  const char = key.domEvent.key;
  if (char === "Enter") {
    ptyProcess.write('\r');
  } else if (char === "Backspace") {
    ptyProcess.write('\b');
  }  else if (char === "Tab") {
    ptyProcess.write('\t');
  } else if (char === "ArrowUp") {
    ptyProcess.write('\x1b[A')
  } else if (char === "ArrowDown") {
    ptyProcess.write('\x1b[B')
  } else if (char === "ArrowRight") {
    ptyProcess.write('\x1b[C')
  } else if (char === "ArrowLeft") {
    ptyProcess.write('\x1b[D')
  } else if (char === "Delete" || char === "Insert" || char === "Home" || char === "End" || char === "PageUp" || char === "PageDown" || char === "Escape" || char === "F1" || char === "F2" || char === "F3" || char === "F4" || char === "F5" || char === "F6" || char === "F7" || char === "F8" || char === "F9" || char === "F10" || char === "F11" || char === "F12") {
    ptyProcess.write('')
  } else if (term.hasSelection() && (key.domEvent.ctrlKey || key.domEvent.CmdKey) && key.domEvent.key === "c") {
    clipboard.writeText(term.getSelected())
  } else if ((key.domEvent.ctrlKey || key.domEvent.CmdKey) && key.domEvent.key === "v") {
    term.focus();
    ptyProcess.write(clipboard.readText())
  } else {
    ptyProcess.write(char);
  }
});

export default class HDDappsUtilityTerminal extends React.Component {
   
  componentDidMount() {
	 
	// Load the Fit Addon and open the Terminal in #xterm terminal-container
	term.loadAddon(fitAddon);
	term.open(document.getElementById('xterm'));
  
    // Make the terminal's size and geometry fit the size of terminal-container
    term.onResize(params => {
      ptyProcess.resize(params.cols, params.rows);
    });
	
	fitAddon.fit();
  }
  
  // Display HODL Terminal and Help / Instructions in the GUI
  render() {
    return (
	
	 <Grid container alignItems="stretch">
	   <Grid xs={12} md={12} lg={12} item>
	   
		  <Flex flexDirection="column" flexGrow="1" alignItems="center">
			
			<DashboardTitle>
				<Link to="/dashboard/hddapps/utilityterminal" color="textPrimary">
					<Trans>HDDcoin Terminal Utility</Trans>
				</Link>
			</DashboardTitle>
			
			<div id="xterm" style={{ height: "85vh", width: "100%" }} />
					
		  </Flex>
		  
		 </Grid>
      </Grid>
    );
  }
}
