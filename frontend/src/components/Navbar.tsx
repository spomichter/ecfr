import React from 'react';
import Link from 'next/link';
import { HomeIcon, ChartBarIcon, MagnifyingGlassIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

type NavbarProps = {
  activePage: 'home' | 'visualizations' | 'search' | 'chat';
};

const Navbar: React.FC<NavbarProps> = ({ activePage }) => {
  const navItems = [
    { name: 'Home', href: '/', icon: HomeIcon, active: activePage === 'home' },
    { name: 'Visualizations', href: '/visualizations', icon: ChartBarIcon, active: activePage === 'visualizations' },
    { name: 'Search', href: '/search', icon: MagnifyingGlassIcon, active: activePage === 'search' },
    { name: 'Chat', href: '/chat', icon: ChatBubbleLeftRightIcon, active: activePage === 'chat' },
  ];

  return (
    <nav className="bg-primary text-white shadow-md">
      <div className="container-custom">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-xl font-heading font-bold">eCFR Analyzer</span>
            </Link>
          </div>
          <div className="hidden md:block">
            <div className="flex items-center space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                    item.active
                      ? 'bg-secondary text-white'
                      : 'text-gray-200 hover:bg-secondary hover:text-white'
                  }`}
                >
                  <item.icon className="h-5 w-5 mr-1" />
                  {item.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className="md:hidden">
        <div className="flex justify-around px-2 pt-2 pb-3 space-x-1">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`flex flex-col items-center px-3 py-2 rounded-md text-xs font-medium ${
                item.active
                  ? 'bg-secondary text-white'
                  : 'text-gray-200 hover:bg-secondary hover:text-white'
              }`}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
