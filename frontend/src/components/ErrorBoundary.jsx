import { Component } from 'react';

/**
 * ErrorBoundary — catches render errors in any child tree.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <SomeComponent />
 *   </ErrorBoundary>
 *
 * Optional props:
 *   fallback  — custom ReactNode shown on error
 *   onError   — callback(error, info) for logging / Sentry
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info);
    this.props.onError?.(error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    if (this.props.fallback) return this.props.fallback;

    const { error } = this.state;

    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        background: 'var(--bg)',
      }}>
        <div style={{
          maxWidth: 480,
          width: '100%',
          background: 'var(--card)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 16,
          padding: '32px 28px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 40, marginBottom: 16 }}>⚠️</div>
          <h2 style={{
            fontSize: 18,
            fontWeight: 700,
            color: 'var(--text)',
            marginBottom: 8,
          }}>
            Something went wrong
          </h2>
          <p style={{
            fontSize: 13,
            color: 'var(--text-2)',
            marginBottom: 24,
            lineHeight: 1.6,
          }}>
            {error?.message || 'An unexpected error occurred.'}
          </p>
          <button
            onClick={this.handleReset}
            style={{
              padding: '10px 24px',
              borderRadius: 10,
              border: 'none',
              background: 'var(--grad)',
              color: '#fff',
              fontWeight: 600,
              fontSize: 14,
              cursor: 'pointer',
            }}
          >
            Try again
          </button>
        </div>
      </div>
    );
  }
}
