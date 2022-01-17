import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex } from '@hddcoin/core';
import { Button, Grid, Typography, Link, Divider } from '@material-ui/core';
import { CardHero } from '@hddcoin/core';
import { HDDappsOnlineStoreHero as HDDappsOnlineStoreHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsOnlineStoreHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsOnlineStore() {
  const history = useHistory();

  function hddAppsLearnMore() {
            window.open(
              "https://store.hddcoin.org", "_blank");
        }

  return (
    <Grid container>
      <Grid xs={12} md={12} lg={12} item>
        <CardHero>
		
          <StyledHDDappsIcon color="primary" />		

          <Typography variant="h5">
            <Trans>
              HDDcoin Online Store
            </Trans>
          </Typography>	

		  <Divider />		  
		  
		  <Typography variant="body1">
			<Trans>
              All merch is currently ON SALE during our Grand Opening / Holiday promotion. 
              Go grab your favorite items quickly while this offer lasts.
              The default Store payment method is HDD. All the major Credit/Debit Cards and PayPal are also accepted.  
			  <Link
                target="_blank"
                href="https://store.hddcoin.org"
              >
                Learn more
			  </Link>
			</Trans>
		  </Typography>
		  		  		  
		  <Flex gap={1}>
            <Button
              onClick={hddAppsLearnMore}
              variant="contained"
              color="primary"
              //fullWidth
            >
              <Trans>Visit Online Store</Trans>
            </Button>
		  </Flex>
		  
        </CardHero>
      </Grid>
    </Grid>
  );
}
