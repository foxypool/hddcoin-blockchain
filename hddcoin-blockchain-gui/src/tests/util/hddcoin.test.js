const hddcoin = require('../../util/hddcoin');

describe('hddcoin', () => {
  it('converts number byte to hddcoin', () => {
    const result = hddcoin.byte_to_hddcoin(1000000);

    expect(result).toBe(0.000001);
  });
  it('converts string byte to hddcoin', () => {
    const result = hddcoin.byte_to_hddcoin('1000000');

    expect(result).toBe(0.000001);
  });
  it('converts number byte to hddcoin string', () => {
    const result = hddcoin.byte_to_hddcoin_string(1000000);

    expect(result).toBe('0.000001');
  });
  it('converts string byte to hddcoin string', () => {
    const result = hddcoin.byte_to_hddcoin_string('1000000');

    expect(result).toBe('0.000001');
  });
  it('converts number hddcoin to byte', () => {
    const result = hddcoin.hddcoin_to_byte(0.000001);

    expect(result).toBe(1000000);
  });
  it('converts string hddcoin to byte', () => {
    const result = hddcoin.hddcoin_to_byte('0.000001');

    expect(result).toBe(1000000);
  });
  it('converts number byte to colouredcoin', () => {
    const result = hddcoin.byte_to_colouredcoin(1000000);

    expect(result).toBe(1000);
  });
  it('converts string byte to colouredcoin', () => {
    const result = hddcoin.byte_to_colouredcoin('1000000');

    expect(result).toBe(1000);
  });
  it('converts number byte to colouredcoin string', () => {
    const result = hddcoin.byte_to_colouredcoin_string(1000000);

    expect(result).toBe('1,000');
  });
  it('converts string byte to colouredcoin string', () => {
    const result = hddcoin.byte_to_colouredcoin_string('1000000');

    expect(result).toBe('1,000');
  });
  it('converts number colouredcoin to byte', () => {
    const result = hddcoin.colouredcoin_to_byte(1000);

    expect(result).toBe(1000000);
  });
  it('converts string colouredcoin to byte', () => {
    const result = hddcoin.colouredcoin_to_byte('1000');

    expect(result).toBe(1000000);
  });
});
