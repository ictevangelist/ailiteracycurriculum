// Prints a JSON map of icon name -> inline SVG markup (currentColor fill).
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const fa = require("react-icons/fa");
const gi = require("react-icons/gi");
const out = {};
for (const n of process.argv.slice(2)) {
  const C = fa[n] || gi[n];
  out[n] = renderToStaticMarkup(React.createElement(C, { size: "1em" }));
}
process.stdout.write(JSON.stringify(out));
