var d3 = require('d3-selection');

function renderMessage({ messageType, message }) {
  var slate = d3.select(`#${messageType}`);
  slate.text(message);
  slate.classed('hidden', false);
}

module.exports = renderMessage;
