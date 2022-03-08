import React from 'react';
import { useSelector } from 'react-redux';
import { Trans } from '@lingui/macro';
import { Link, Table, Card, FormatBytes } from '@hddcoin/core';
import { Typography } from '@material-ui/core';
import moment from 'moment';
import type { Row } from '../core/components/Table/Table';
import usePlots from '../../hooks/usePlots';
import { RootState } from '../../modules/rootReducer';
import ProofGraph from "./ProofGraph"
import styled from 'styled-components';

const StyledGraphContainer = styled.div`
  margin-left: 0rem;
  margin-right: 0rem;
  margin-top: 1rem;
  margin-bottom: -1rem;
`;

// function hashFnv32a(str, asString = true, seed = undefined) {
//   /*jshint bitwise:false */
//   let  i, l,hval = (seed === undefined) ? 0x811c9dc5 : seed;

//   for (i = 0, l = str.length; i < l; i++) {
//     hval ^= str.charCodeAt(i);
//     hval += (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
//   }
//   if (asString) {
//     // Convert to 8 digit hex string
//     return ("0000000" + (hval >>> 0).toString(16)).substr(-8).toUpperCase();
//   }
//   return hval >>> 0;
// }

const cols = [
  {
    minWidth: '200px',
    field: 'challenge_hash',
    tooltip: true,
    title: <Trans>Challenge</Trans>,
  },
//  {
//    tooltip(row: Row) {
//      return row.signage_point
//    },
//    field(row: Row) {
//      return hashFnv32a(row.signage_point)
//    },
//    title: <Trans>Signage Point</Trans>,
//  },
  {
    field(row: Row) {
      return `${row.passed_filter} / ${row.total_plots}`;
    },
    title: <Trans>Plots Passed Filter</Trans>,
  },
  {
    field: 'proofs',
    title: <Trans>Proofs Found</Trans>,
  },
  {
    field: 'time_elapsed',
    title: <Trans>Lookup Time</Trans>,
  },
//  {
//    field: 'interval',
//    title: <Trans>Interval</Trans>,
//  },
  {
    field(row: Row) {
      return moment(row.timestamp * 1000).format('MMM D, h:mm:ss A');
    },
    title: <Trans>Date</Trans>,
  },
];

export default function FarmLastAttemptedProof() {
  const { size } = usePlots();

  const lastAttemptedProof = useSelector(
    (state: RootState) => state.farming_state.farmer.last_farming_info ?? [],
  );

  // const { lastAttemptedProof, signagePoints } = useSelector((state: RootState) => {
  //   return {
  //     lastAttemptedProof: state.farming_state.farmer.last_farming_info ?? [],
  //     signagePoints: state.farming_state.farmer.signage_points ?? [],
  //     updated:Date.now()
  //   }
  // }, (a,b)=>{
  //   if(((a||{updated:0}).updated - (b||{updated:0}).updated)>5000){
  //     return false
  //   }
  //   return true
  // })

  // let reducedLastAttemptedProof = lastAttemptedProof.map(cur => {
  //   cur.spts = cur.timestamp
  //   let sp = signagePoints.find(signage => {
  //     return (signage.signage_point.challenge_hash == cur.challenge_hash) && (cur.signage_point == signage.signage_point.challenge_chain_sp)
  //   })
  //   if (sp) {
  //     cur.spts = sp.timestamp
	//   cur.duration = (cur.timestamp - (sp.timestamp / 1000)).toFixed(4) || 0.00
  //     cur.interval = sp.interval ? sp.interval / 1000 : null
  //   }
  //   return cur
  // })

  // reducedLastAttemptedProof = reducedLastAttemptedProof.sort((a, b) => b.spts - a.spts)
  const reducedLastAttemptedProof = lastAttemptedProof.slice(0, 5).sort((a,b) => a.timestamp-b.timestamp);
  const reducedProofLookups = lastAttemptedProof.slice(0, 200).sort((a,b) => a.timestamp-b.timestamp);
  let graphProofPoints = []
  for (let i = 0; i < reducedProofLookups.length; i++) {
    let cur = reducedProofLookups[reducedProofLookups.length - i - 1]
    graphProofPoints.push([cur.timestamp, cur.time_elapsed])

  }
  graphProofPoints = graphProofPoints.sort((a, b) => b.timestamp - a.timestamp)
  const isEmpty = !reducedLastAttemptedProof.length;

  return (
    <Card
      title={<Trans>Last Attempted Proof</Trans>}
      tooltip={
        <Trans>
          This table shows you the last time your farm attempted to win a block
          challenge.{' '}
          <Link
            target="_blank"
            href="https://github.com/HDDcoin-Network/hddcoin-blockchain/wiki/FAQ#what-is-the-plot-filter-and-why-didnt-my-plot-pass-it"
          >
            Learn more
          </Link>
        </Trans>
      }
      interactive
    >
      <StyledGraphContainer>
        {(graphProofPoints.length>3) && (<ProofGraph points={graphProofPoints} />)}
      </StyledGraphContainer>
      <Table
        pages
        rowsPerPageOptions={[5, 10, 25, 100]}
        rowsPerPage={5}
        cols={cols}
        rows={reducedLastAttemptedProof}
        caption={
          isEmpty && (
            <Typography>
              <Trans>None of your plots have passed the plot filter yet.</Trans>

              {!!size && (
                <>
                  {' '}
                  <Trans>
                    But you are currently farming{' '}
                    <FormatBytes value={size} precision={3} />
                  </Trans>
                </>
              )}
            </Typography>
          )
        }
      />
    </Card>
  );
}
