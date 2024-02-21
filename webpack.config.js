const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  context: __dirname,
  entry: "./django_web_repl/static/django_web_repl/js/terminal",
  cache: false,
  output: {
    path: path.resolve(
      __dirname,
      "django_web_repl/static/django_web_repl/output",
    ),
    publicPath: "auto", // necessary for CDNs/S3/blob storages
    filename: "terminal.js",
  },
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "terminal.css",
    }),
    new BundleTracker({ path: __dirname, filename: "webpack-stats.json" }),
  ],
};
