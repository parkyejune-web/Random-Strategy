import Link from 'next/link';

const links = [
  ['/', 'Home'],
  ['/youtube', 'YouTube'],
  ['/news', 'News'],
  ['/drafts', 'Drafts'],
  ['/settings', 'Settings']
];

export default function Nav() {
  return (
    <nav className="nav">
      {links.map(([href, label]) => (
        <Link key={href} href={href}>{label}</Link>
      ))}
    </nav>
  );
}
