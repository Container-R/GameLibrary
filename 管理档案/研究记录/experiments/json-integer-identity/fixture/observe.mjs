// Actual built-in observations only; no expected-result table or imports.
const input = ['9007199254740992', '9007199254740993'];
const number = input.map(text => JSON.parse(text));
const stringInput = input.map(text => '"' + text + '"');
const strings = stringInput.map(text => JSON.parse(text));
const convertedStrings = number.map(value => String(value));
const convertedBigints = number.map(value => BigInt(value));
const textBigints = input.map(text => BigInt(text));
const stringify = {
  input_text: input[1], threw: false, error_name: null,
  returned: false, return_type: null, return_value: null
};
try {
  const result = JSON.stringify(textBigints[1]);
  stringify.returned = true;
  stringify.return_type = typeof result;
  stringify.return_value = result === undefined ? null : result;
} catch (error) {
  stringify.threw = true;
  stringify.error_name = error.name;
}
const observations = {
  number_parse: number.map((value, i) => ({input_text: input[i], type: typeof value,
    decimal: String(value), safe_integer: Number.isSafeInteger(value)})),
  number_equal: number[0] === number[1],
  string_parse: strings.map((value, i) => ({input_text: stringInput[i], type: typeof value, value})),
  string_equal: strings[0] === strings[1],
  string_from_number: convertedStrings.map(value => ({type: typeof value, value})),
  string_from_number_equal: convertedStrings[0] === convertedStrings[1],
  bigint_from_number: convertedBigints.map(value => ({type: typeof value, decimal: String(value)})),
  bigint_from_number_equal: convertedBigints[0] === convertedBigints[1],
  bigint_from_text: textBigints.map((value, i) => ({input_text: input[i], type: typeof value, decimal: String(value)})),
  bigint_from_text_equal: textBigints[0] === textBigints[1],
  default_bigint_stringify: stringify
};
console.log(JSON.stringify({schema: 'json-integer-identity-v1', node_version: process.version, observations}));
