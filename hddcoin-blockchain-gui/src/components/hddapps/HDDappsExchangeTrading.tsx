import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex } from '@hddcoin/core';
import { Button, Grid, Typography, Link, Divider } from '@material-ui/core';
import { CardHero } from '@hddcoin/core';
import { HDDappsExchangeTradingHero as HDDappsExchangeTradingHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsExchangeTradingHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsExchangeTrading() {
  const history = useHistory();

  function hddAppsLearnMore() {
            window.open(
              "https://hddcoin.org/exchanges", "_blank");
        }
		
  function hddAppsTradeHDD() {
            window.open(
              "https://www.xt.com/trade/hdd_usdt", "_blank");
        }


  return (
    <Grid container>
      <Grid xs={12} md={12} lg={12} item>
        <CardHero>
		
          <StyledHDDappsIcon color="primary" />
		  
		  <Typography variant="h5">
		    <Trans>
			  HDDcoin Exchange Trading
			</Trans>
          </Typography>
		  
		  <Divider />
		  
          <Typography variant="body1">
            <Trans>              
              The HDD/USDT pair is currently trading on XT.com, a top-20 Exchange with great reputation, 
              trading volumes, and customer support. XT.com has over 2 million registered users, 
			  more than 200,000 active users monthly, and more than 7 million users in its ecosystem.  
			  <Link
                target="_blank"
                href="https://hddcoin.org/exchanges"
              >
                Learn more
			 </Link>
            </Trans>
          </Typography>
		  	
		  <Flex gap={1}>
            <Button
              onClick={hddAppsTradeHDD}
              variant="contained"
              color="primary"
              fullWidth
            >
              <Trans>Trade HDD Now</Trans>
            </Button>
			
            <Button
              onClick={hddAppsLearnMore}
              variant="outlined"
              color="primary"
              fullWidth
            >
              <Trans>Learn about Exchanges</Trans>
            </Button>
          </Flex>	  
		  
        </CardHero>
      </Grid>
    </Grid>
  );
}
