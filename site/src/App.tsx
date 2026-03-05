import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { DocsPage } from "./pages/DocsPage";
import { BenchmarksPage } from "./pages/BenchmarksPage";
import { AboutPage } from "./pages/AboutPage";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path='/' element={<HomePage />} />
          <Route path='/benchmarks' element={<BenchmarksPage />} />
          <Route path='/docs' element={<DocsPage />} />
          <Route path='/about' element={<AboutPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
