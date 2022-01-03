import * as React from 'react';
import DashboardTitle from '../dashboard/DashboardTitle';
import { Flex } from '@hddcoin/core';
import { Paper } from '@material-ui/core';
import styled from 'styled-components';
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import 'xterm/css/xterm.css';
import c from "ansi-colors";
import path from 'path';
import { existsSync, readFileSync } from 'fs';
import { Trans } from '@lingui/macro';
import ScrollToBottom from 'react-scroll-to-bottom';
							
const PY_MAC_DIST_FOLDER = '../../../app.asar.unpacked/daemon';
const PY_WIN_DIST_FOLDER = '../../../app.asar.unpacked/daemon';
const HODL_HELP_PATH = process.env[(process.platform === 'win32') ? 'USERPROFILE' : 'HOME'] + '/.hddcoin/mainnet/hodl/hodlhelp.txt';
const fullPath = (existsSync((process.platform === 'win32') ? path.join(__dirname, PY_WIN_DIST_FOLDER) : path.join(__dirname, PY_MAC_DIST_FOLDER))) ? ((process.platform === 'win32') ? path.join(__dirname, PY_WIN_DIST_FOLDER) : path.join(__dirname, PY_MAC_DIST_FOLDER)) : path.join(__dirname, '../../../venv/bin');
const ENV_HDDCOIN = ((process.platform === 'win32') ? '$env:Path += ";' : 'export PATH="$PATH:') + fullPath + '"';
const SHELL = (process.platform === 'win32') ? 'powershell.exe' : 'bash';
const pty = require('node-pty');

// HODL Help / Instructions Stylying
const StyledPaper = styled(Paper)`
  color: #37c3fe;
  min-width: 84%;
  height: 35vh;
  bottom: 0;
  font-size: 14px;
  background-color: #2b2a2a;
  border-top: 2px solid #3db6ea;
  border-bottom: 2px solid #3db6ea;
  padding-top: 4px;
  padding-bottom: 2px;
  padding-left: 2px;
  pre {
	font-size: 14px;
  }
`;

const StyledScrollToBottom = styled(ScrollToBottom)`
  width: 100%;
  height: 100%;
`;

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
ptyProcess.write('hddcoin hodl -h\r');

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
  } else if (char === "ArrowUp") {
    ptyProcess.write('\x1b[A')
  } else if (char === "ArrowDown") {
    ptyProcess.write('\x1b[B')
  } else if (char === "ArrowRight") {
    ptyProcess.write('\x1b[C')
  } else if (char === "ArrowLeft") {
    ptyProcess.write('\x1b[D')
  } else if (term.hasSelection() && key.key === "�") {
    document.execCommand('copy') 
  } else {
    ptyProcess.write(char);
  }
});

// Write text inside the terminal
// term.write('Welcome to ' + c.green('HDDcoin') + ' HODL Terminal Console\r\n');
// term.write('Daemon directory: ' + c.green(fullPath) + '\r\n');

export default class HODLterminal extends React.Component {
  constructor(props) {
    super(props);	
	this.state = {
      hodlhelp: "Loading HODL Help / Instructions...",
	};
  }
  
  // Read content of hodlhelp.txt
  checkHODLhelpFile() {

    if (existsSync(HODL_HELP_PATH)) {
      const buffer = readFileSync(HODL_HELP_PATH);
      const hodlhelpContent = buffer.toString();
      this.setState({hodlhelp: hodlhelpContent});
    }
  }
  
  componentDidMount() {
	  
	// Load HODL Help / Instructions
	this.checkHODLhelpFile();
	 
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
      <Flex flexDirection="column" flexGrow="1">

        <DashboardTitle>
            <Trans>HDDcoin HODL and Apps Terminal</Trans>
        </DashboardTitle>
		
		<div id="xterm" style={{ height: "55vh", width: "100%"}} />
		
		<StyledPaper>
			<StyledScrollToBottom>
				<pre>{this.state.hodlhelp}</pre>
			</StyledScrollToBottom>
        </StyledPaper>
				
      </Flex>
    );
  }
}
