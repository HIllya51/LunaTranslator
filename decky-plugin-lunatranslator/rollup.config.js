import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import importAssets from "rollup-plugin-import-assets";

import { defineConfig } from "rollup";

export default defineConfig({
  input: "src/index.tsx",
  plugins: [
    commonjs(),
    nodeResolve(),
    typescript(),
    json(),
    replace({
      preventAssignment: false,
      "process.env.NODE_ENV": JSON.stringify("production"),
    }),
    importAssets({
      publicPath: "http://127.0.0.1:1337/plugins/LunaTranslator Overlay/",
    }),
  ],
  context: "window",
  external: ["react", "react-dom"],
  output: {
    file: "dist/index.js",
    globals: {
      react: "SP_REACT",
      "react-dom": "SP_REACTDOM",
    },
    format: "iife",
    exports: "default",
  },
});
