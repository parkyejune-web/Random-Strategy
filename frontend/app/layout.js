import './globals.css';
import Nav from '../components/Nav';

export const metadata = {
  title: 'Automation MVP Dashboard'
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <div className="container">
          <Nav />
          {children}
        </div>
      </body>
    </html>
  );
}
