import { ChatPage } from './pages/ChatPage'
import { SignInPage } from './pages/SignInPage'
import { useAuth } from './hooks/useAuth'

function App() {
  const auth = useAuth()

  if (!auth.isAuthenticated) {
    return (
      <SignInPage
        step={auth.step}
        email={auth.email}
        isLoading={auth.isLoading}
        error={auth.error}
        onSubmitEmail={auth.submitEmail}
        onSubmitCode={auth.submitCode}
        onResend={auth.resendCode}
      />
    )
  }

  return <ChatPage />
}

export default App
