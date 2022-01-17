import React from 'react';
import { Route, Switch, useRouteMatch } from 'react-router-dom';
import LayoutMain from '../layout/LayoutMain';
import { Trans } from '@lingui/macro';
import { Flex, Link } from '@hddcoin/core';
import { Grid, Typography } from '@material-ui/core';
import HDDappsHODL from './HDDappsHODL';
import HDDappsOnlineStore from './HDDappsOnlineStore';
import HDDappsNFTMarketPlace from './HDDappsNFTMarketPlace';
import HDDappsExchangeTrading from './HDDappsExchangeTrading';
import HDDappsUtility from './HDDappsUtility';
import HDDappsApplications from './HDDappsApplications';

import HDDappsHODLTerminal from './HDDappsHODLTerminal';
import HDDappsUtilityTerminal from './HDDappsUtilityTerminal';
import HDDappsUtilityLogs from './HDDappsUtilityLogs';

export default function HDDapps() {
	
  const { path } = useRouteMatch();

  return (
  
    <LayoutMain 
		
      title={
        <>
          <Link to="/dashboard/hddapps" color="textPrimary">
            <Trans>HDDcoin Applications and Utilities</Trans>
          </Link>
        </>
      }
	>	
	
		<>	
		<Flex flexDirection="column" gap={1} alignItems="center">
		
			<Switch>
			  
			  <Route path={path} exact>
				<div>
				
				  <Grid container spacing={4} alignItems="stretch">
				  
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsHODL />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsOnlineStore />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsNFTMarketPlace />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsExchangeTrading />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsUtility />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsApplications />
					</Grid>
					
				  </Grid>
				  
				</div>

			  </Route>
			  
			  <Route path={`${path}/hodlterminal`} exact>
				<HDDappsHODLTerminal />
			  </Route>
			  
			  <Route path={`${path}/utilityterminal`} exact>
				<HDDappsUtilityTerminal />
			  </Route>
			  
			  <Route path={`${path}/utilitylogs`} exact>
				<HDDappsUtilityLogs />
			  </Route>
			  
			</Switch>

		</Flex>	     
		</> 
	 
    </LayoutMain>
  );
}
