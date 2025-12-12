import { useState } from 'react';
import { getErrorLogs } from '../services/api';

interface ErrorDisplayProps {
  error: string;
  requestId?: string | null;
  prompt?: string | null;
  provider?: string | null;
  errorType?: 'generation' | 'execution' | 'validation' | 'other';
  showReportButton?: boolean;
  onReportClick?: () => void;
}

export function ErrorDisplay({
  error,
  requestId,
  prompt,
  provider,
  errorType = 'other',
  showReportButton = true,
  onReportClick
}: ErrorDisplayProps) {
  const [isReporting, setIsReporting] = useState(false);

  const handleReportError = async () => {
    setIsReporting(true);
    
    try {
      // Fetch logs if request_id available
      let logs = '';
      if (requestId) {
        try {
          const logData = await getErrorLogs(requestId);
          logs = logData.logs.join('\n');
        } catch (e) {
          logs = 'Unable to retrieve logs from server';
        }
      }

      // Format email body
      const emailBody = `
Error Report Details:
- Request ID: ${requestId || 'N/A'}
- Timestamp: ${new Date().toISOString()}
- Provider: ${provider || 'N/A'}
- Error Type: ${errorType}

User Prompt/Code:
${prompt || 'N/A'}

Frontend Error:
${error}

Backend Logs (last 50 lines):
${logs || 'No logs available'}

User Agent: ${navigator.userAgent}
      `.trim();

      const subject = `[Diagram Generator] Error Report - ${requestId || 'Unknown'}`;
      const recipient = import.meta.env.VITE_ERROR_REPORT_EMAIL || 'your-email@example.com';
      
      // Create mailto link
      const mailtoLink = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`;
      
      // Open email client
      window.location.href = mailtoLink;
      
      if (onReportClick) {
        onReportClick();
      }
    } catch (err) {
      console.error('Failed to generate error report:', err);
      alert('Failed to generate error report. Please copy the error details manually.');
    } finally {
      setIsReporting(false);
    }
  };

  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <p className="text-sm text-red-600 break-words">{error}</p>
        </div>
        {showReportButton && (
          <button
            onClick={handleReportError}
            disabled={isReporting}
            className="flex-shrink-0 inline-flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-all"
          >
            {isReporting ? (
              <>
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Preparing...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Report Error
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

