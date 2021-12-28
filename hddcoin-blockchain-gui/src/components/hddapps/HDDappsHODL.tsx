import * as React from 'react';
import DashboardTitle from '../dashboard/DashboardTitle';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Button, Grid, Typography } from '@material-ui/core';
import { CardHero } from '@hddcoin/core';
import { HDDapps as HDDappsIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsIcon)`
  font-size: 4rem;
`;

export default function HDDappsHODL() {
  const history = useHistory();

  function handleVisitHDDcoinHODL() {
  }

  return (
    <Grid container>
      <Grid xs={12} md={6} lg={5} item>
        <CardHero>
          <StyledPoolIcon color="primary" />
          <Typography variant="body1">
            <Trans>
              Lock your coins and get huge rewards up to thirty percent HDDcoin HODL Program allows Coin Holders to earn rewards on HDD locked a Smart Contract a specific hold duration
            </Trans>
          </Typography>
          <Button onClick={handleVisitHDDcoinHODL} variant="contained" color="primary">
            <Trans>Join HDDcoin HODL Program</Trans>
          </Button>
        </CardHero>
      </Grid>
    </Grid>
  );
}
