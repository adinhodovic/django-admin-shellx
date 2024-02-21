const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { warn } = require("console");

module.exports = {
  context: __dirname,
  entry: "./django_admin_shellx/static/django_admin_shellx/js/terminal",
  output: {
    path: path.resolve(
      __dirname,
      "django_admin_shellx/static/django_admin_shellx/output",
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
  ],
};
