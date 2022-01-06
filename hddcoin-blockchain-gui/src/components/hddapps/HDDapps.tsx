import React from 'react';
import { Trans } from '@lingui/macro';
import { Route, Switch, useRouteMatch } from 'react-router-dom';
import { Flex, Link } from '@hddcoin/core';
import LayoutMain from '../layout/LayoutMain';
import HDDappsHODL from './HDDappsHODL';
import HDDappsTerminal from './HDDappsTerminal';
import DashboardTitle from '../dashboard/DashboardTitle';
import { Paper } from '@material-ui/core';
import path from 'path';

export default function HDDapps() {
  const { path } = useRouteMatch();

  return (
    <LayoutMain
      title={
        <>
          <Link to="/dashboard/hddapps" color="textPrimary">
            <Trans>HDD Apps</Trans>
          </Link>
        </>
      }
    >
	
      <Flex flexDirection="column" gap={3}>
	  
        <Switch>
		
		  <DashboardTitle>
			<Trans>HDDcoin HODL Program</Trans>
		  </DashboardTitle>
		
		  <Route path={path} exact>
            <HDDappsHODL />
          </Route>		 
		  
		  <DashboardTitle>
			<Trans>HDDcoin Terminal</Trans>
		  </DashboardTitle>
			
		  <Route path={path} exact>
            <HDDappsTerminal />
          </Route>
		  
        </Switch>
		
      </Flex>
	  
    </LayoutMain>
  );
}
