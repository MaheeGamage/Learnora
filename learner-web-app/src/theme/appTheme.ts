import { createTheme } from "@mui/material/styles";

const appTheme = createTheme({
  cssVariables: {
    colorSchemeSelector: "data-toolpad-color-scheme",
  },
  colorSchemes: { light: true, dark: false },
});

export default appTheme;
