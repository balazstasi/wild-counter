import { Layout } from "@/components/composed/layout";
import { ThemeProvider } from "@/components/composed/theme-provider";

function App() {
  return (
    <ThemeProvider>
      <Layout />
    </ThemeProvider>
  );
}

export default App;
