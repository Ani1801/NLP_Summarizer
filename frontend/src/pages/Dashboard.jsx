import React from 'react';
import StatCards from '../components/StatCards';
import { useAuth } from '../context/AuthContext';
import RecentAudits from '../components/RecentAudits';
import ActionItems from '../components/ActionItems';

const Dashboard = () => {
  const { user } = useAuth();
  const userName = user?.name ? user.name.split(' ')[0] : 'Patrick';

  return (
    <div className="p-8 max-w-[1400px] mx-auto w-full flex-1">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Good morning, {userName}</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">You have 2 pending actions and 1 new critical risk highlighted.</p>
      </div>
      
      <StatCards />
      
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <RecentAudits />
        </div>
        <div className="lg:col-span-4">
          <ActionItems />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
