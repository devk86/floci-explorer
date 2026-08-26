import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { DashboardPage } from './pages/Dashboard'
import { InfrastructurePage } from './pages/Infrastructure'
import { ResourceDetailsPage } from './pages/ResourceDetails'
import { ResourcesPage } from './pages/Resources'
import { TerraformPage } from './pages/Terraform'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/infrastructure" element={<InfrastructurePage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/resources/:service/:resourceId" element={<ResourceDetailsPage />} />
          <Route path="/terraform" element={<TerraformPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
