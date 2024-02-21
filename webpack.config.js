const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { warn } = require("console");

module.exports = {
  context: __dirname,
  entry: "./django_custom_admin/static/django_custom_admin/js/terminal",
  output: {
    path: path.resolve(
      __dirname,
      "django_custom_admin/static/django_custom_admin/output",
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
