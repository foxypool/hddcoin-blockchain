import * as React from 'react';
import DashboardTitle from '../dashboard/DashboardTitle';
import { Flex } from '@hddcoin/core';
import { Paper, Grid } from '@material-ui/core';
import styled from 'styled-components';
import { existsSync, readFileSync } from 'fs';
import { Trans } from '@lingui/macro';
import ScrollToBottom from 'react-scroll-to-bottom';							
const HDDCOIN_LOG_PATH = process.env[(process.platform === 'win32') ? 'USERPROFILE' : 'HOME'] + '/.hddcoin/mainnet/log/debug.log';

// HDDcoin Logs Stylying
const StyledPaper = styled(Paper)`
  color: #37c3fe;
  min-width: 90%;
  height: 85vh;
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

export default class HDDappsUtilityLogs extends React.Component {
 
 constructor(props) {
    super(props);	
	this.state = {
      hddcoinLog: "Loading HDDcoin Logs...",
	  logTimer: 0,
	};
  }
  
  // Read content of debug.log
  checkHDDcoinLogFile() {

    if (existsSync(HDDCOIN_LOG_PATH)) {
      const buffer = readFileSync(HDDCOIN_LOG_PATH);
      const hddcoinLogContent = buffer.toString();
      this.setState({hddcoinLog: hddcoinLogContent});
    }
  }
  
  componentWillUnmount() {
    clearInterval(this.state.logTimer);
  }
  
  componentDidMount() {
	  
	// Load HDDcoin Logs
	let logCheckTimer = setInterval(() => this.checkHDDcoinLogFile(), 3000);
	this.checkHDDcoinLogFile();
    this.setState({logTimer: logCheckTimer});
  }
  
  // Display HDDcoin Logs in the GUI
  
 render() {
    return (
	
	 <Grid container alignItems="stretch">
	   <Grid xs={12} md={12} lg={12} item>
	   
		  <Flex flexDirection="column" flexGrow="1">

			<DashboardTitle>
				<Trans>HDDcoin Logs Utility</Trans>
			</DashboardTitle>
				
			<StyledPaper>
				<StyledScrollToBottom debug={false}>
					<pre>{this.state.hddcoinLog}</pre>
				</StyledScrollToBottom>
			</StyledPaper>
					
		  </Flex>
		</Grid>
	 </Grid>
    );  
  }
}
