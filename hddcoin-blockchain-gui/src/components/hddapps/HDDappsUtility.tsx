import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex, CardHero } from '@hddcoin/core';
import { Button, Grid, Typography, Divider } from '@material-ui/core';
import { HDDappsUtilityHero as HDDappsUtilityHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsUtilityHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsUtility() {
  const history = useHistory();

   function hddAppsOpenTerminal() {
	history.push('/dashboard/hddapps/utilityterminal');
  }
  
   function hddAppsOpenLogs() {
	history.push('/dashboard/hddapps/utilitylogs');
  }
  
  return (
    <Grid container>
	  <Grid xs={12} md={12} lg={12} item>
	  
        <CardHero>		  
		  
		  <StyledHDDappsIcon color="primary" />		

          <Typography variant="h5">
            <Trans>
              HDDcoin Utility Tools
            </Trans>
          </Typography>	

		  <Divider />		  
		  
		  <Typography variant="body1">
			<Trans>
			{'The HDDcoin Terminal Utility opens directly in the GUI, enabling users to conveniently work in Command Line. The HDDcoin Client Logs Utility opens directly in the GUI, with the logs updated in real time. More HDDcoin Utility Tools are under development.'}
			</Trans>
		  </Typography>
		  
		  <Flex gap={1}>
            <Button
              onClick={hddAppsOpenTerminal}
              variant="contained"
              color="primary"
              fullWidth
            >
              <Trans>Open Terminal</Trans>
            </Button>
			
            <Button
              onClick={hddAppsOpenLogs}
              variant="outlined"
              color="primary"
              fullWidth
            >
              <Trans>Open Client Logs</Trans>
            </Button>
          </Flex>
		  
        </CardHero>
      </Grid>
    </Grid>
  );
}
