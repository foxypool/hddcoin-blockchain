import React from 'react';
import { shell } from 'electron';
import styled from 'styled-components';
import { Route, Switch, useRouteMatch } from 'react-router';
import { withRouter } from 'react-router-dom'
import { AppBar, Toolbar, Drawer, Divider, Typography } from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import {
  DarkModeToggle,
  LocaleToggle,
  Flex,
  Logo,
  ToolbarSpacing,
} from '@hddcoin/core';
import { defaultLocale, locales } from '../../config/locales';
import Wallets from '../wallet/Wallets';
import FullNode from '../fullNode/FullNode';
import Plot from '../plot/Plot';
import Farm from '../farm/Farm';
import Pool from '../pool/Pool';
import HODLterminal from '../hodlterminal/HODLterminal';
import HDDapps from '../hddapps/HDDapps';
import Block from '../block/Block';
import Settings from '../settings/Settings';
import DashboardSideBar from './DashboardSideBar';
import { DashboardTitleTarget } from './DashboardTitle';
import TradeManager from '../trading/TradeManager';
import BackupCreate from '../backup/BackupCreate';

const StyledRoot = styled(Flex)`
  height: 100%;
  // overflow: hidden;
`;

const StyledAppBar = styled(AppBar)`
  background-color: ${({ theme }) =>
    theme.palette.type === 'dark' ? '#424242' : 'white'};
  box-shadow: 0px 0px 8px rgba(0, 0, 0, 0.2);
  width: ${({ theme }) => `calc(100% - ${theme.drawer.width})`};
  margin-left: ${({ theme }) => theme.drawer.width};
  z-index: ${({ theme }) => theme.zIndex.drawer + 1};
`;

const StyledDrawer = styled(Drawer)`
  z-index: ${({ theme }) => theme.zIndex.drawer + 2};
  width: ${({ theme }) => theme.drawer.width};
  flex-shrink: 0;

  > div {
    width: ${({ theme }) => theme.drawer.width};
  }
`;

const StyledBody = styled(Flex)`
  min-width: 0;
`;

const StyledBrandWrapper = styled(Flex)`
  height: 64px;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  // border-right: 1px solid rgba(0, 0, 0, 0.12);
`;

const StyledValue = styled(Typography)`
  cursor: pointer;
  font-size: 1.2rem;
  color: primary;
  border-style: solid;
  border-width: 1px;
  border-color: primary;
  border-radius: 5px;
  margin-right: 1.5em;
  padding-right: 1.5em;
  padding-left: 1.5em;
`;

const https = require('https');
const electron = require("electron");
const app = electron.app || electron.remote.app;
const version = app.getVersion();

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      display: "none",
      severity: "info",
      last_version: "Check..",
      exch_rate: "Checking...",
      link: "No-link",
      timerID: 0,
    };
  }

  updateClick = (event) => {
    if ( this.state.severity === 'warning') {
      shell.openExternal("https://github.com/HDDcoin-Network/hddcoin-blockchain/releases/latest");
    }
  }

  exchangeClick = (event) => {
    shell.openExternal("https://www.coingecko.com/en/coins/hddcoin");
  }

  checkUpdate() {
    console.log('AppVersion:',version);
    const options = {
      headers: { 'User-Agent': 'Mozilla/5.0' }
    };

    https.get(
      'https://api.github.com/repos/HDDcoin-Network/hddcoin-blockchain/releases/latest', options, (resp) =>{
        let data = '';
        resp.on('data', (chunk) =>{
          data += chunk;
        });
        resp.on('end', () =>{
          console.log(data);
          var respParsed = JSON.parse(data);
          if (respParsed.tag_name <= version) {
            this.setState({severity: 'info'});
            this.setState({last_version: 'No updates available'});
            this.setState({display: 'none'});
          } else {
            this.setState({severity: 'warning'});
            this.setState({last_version: 'Update available!'});
            this.setState({display: 'flex'});
          }
        });
      }).on("error", (err) => {
        console.log("Error: " + err.message);
      });
  }

  checkExchange() {
    const options = {
      headers: { 'User-Agent': 'Mozilla/5.0' }
    };

    https.get(
      // 'https://api.xt.com/data/api/v1/getTicker?market=hdd_usdt', options, (resp) =>{
      'https://api.coingecko.com/api/v3/coins/hddcoin?localization=false&tickers=false&market_data=true&developer_data=false&sparkline=false', options, (resp) =>{
        let data = '';
        resp.on('data', (chunk) =>{
          data += chunk;
        });
        resp.on('end', () =>{
          console.log(data);
          var respParsed = JSON.parse(data);
          // if (respParsed.price) {
          if (respParsed.market_data.current_price.usd) {
            this.setState({exch_rate: 'HDD/USD: $' + respParsed.market_data.current_price.usd.toFixed(2)});
          } else {
            this.setState({exch_rate: 'HDD/USD: ...'});
          }
        });
      }).on("error", (err) => {
        console.log("Error: " + err.message);
        this.setState({exch_rate: 'Checking...'});
      });
  }

  runCheckers() {
    this.checkUpdate();
    this.checkExchange();
  }

  componentWillUnmount() {
    clearInterval(this.state.timerID); 
  }

  componentDidMount() {
    let tID = setInterval(() => this.runCheckers(), 900000); // check every 15 mins
    this.setState({timerID: tID});
    this.runCheckers();
  }

  render() {
    //const { path } = useRouteMatch();
    const { path } = this.props.match;
    return (
      <StyledRoot>
        <BackupCreate />
        <StyledAppBar position="fixed" color="transparent" elevation={0}>
          <Toolbar>
            <DashboardTitleTarget />
            <Flex flexGrow={1} />
            <StyledValue onClick={this.exchangeClick}>{this.state.exch_rate}</StyledValue>
            <LocaleToggle locales={locales} defaultLocale={defaultLocale} />
            <Alert style={{cursor:'pointer', display:this.state.display}} severity={this.state.severity} onClick={this.updateClick}>{this.state.last_version}</Alert>
            <DarkModeToggle />
          </Toolbar>
        </StyledAppBar>
        <StyledDrawer variant="permanent">
          <StyledBrandWrapper>
            <Logo width={2 / 3} />
          </StyledBrandWrapper>
          <Divider />
          <DashboardSideBar />
        </StyledDrawer>
        <StyledBody flexDirection="column" flexGrow={1}>
          <ToolbarSpacing />
          <Switch>
            <Route path={`${path}`} exact>
              <FullNode />
            </Route>
            <Route path={`${path}/block/:headerHash`} exact>
              <Block />
            </Route>
            <Route path={`${path}/wallets/:walletId?`}>
              <Wallets />
            </Route>
            <Route path={`${path}/plot`}>
              <Plot />
            </Route>
            <Route path={`${path}/farm`}>
              <Farm />
            </Route>
            <Route path={`${path}/pool`}>
              <Pool />
            </Route>
            <Route path={`${path}/hodlterminal`}>
              <HODLterminal />
            </Route>	  
            <Route path={`${path}/hddapps`}>
              <HDDapps />
            </Route>	  
            <Route path={`${path}/trade`}>
              <TradeManager />
            </Route>
            <Route path={`${path}/settings`}>
              <Settings />
            </Route>
          </Switch>
        </StyledBody>
      </StyledRoot>
    );}
}

export default withRouter(Dashboard);
