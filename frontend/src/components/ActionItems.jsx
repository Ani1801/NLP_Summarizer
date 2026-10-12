import React, { useState } from 'react';

const ActionItems = () => {
  const [items, setItems] = useState([
    { id: 1, text: 'Review non-compete duration in Smith contract', done: false, priority: 'High' },
    { id: 2, text: 'Run GDPR compliance check on User Data Policy', done: false, priority: 'Medium' },
    { id: 3, text: 'Export monthly risk summary report to PDF', done: true, priority: 'Normal' },
    { id: 4, text: 'Finalize template for standard SaaS SLA', done: true, priority: 'Normal' }
  ]);

  const toggleItem = (id) => {
    setItems(items.map(item => item.id === id ? { ...item, done: !item.done } : item));
  };

  const pendingCount = items.filter(i => !i.done).length;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200/60 dark:border-slate-800 overflow-hidden h-full flex flex-col transition-colors duration-200">
      <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-800 dark:text-white tracking-tight">Action Items</h2>
        <span className="bg-blue-100 dark:bg-blue-900/40 text-primary-blue dark:text-blue-400 text-xs font-bold px-2.5 py-1 rounded-full">{pendingCount} Pending</span>
      </div>
      
      <div className="p-2 flex-1 outline-none">
        <ul className="space-y-1">
          {items.map(item => (
            <li 
              key={item.id} 
              className={`flex items-start gap-3 p-4 rounded-lg transition-colors cursor-pointer ${
                item.done ? 'bg-transparent' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
              }`}
              onClick={() => toggleItem(item.id)}
            >
              <div className="mt-0.5">
                <input
                  type="checkbox"
                  checked={item.done}
                  onChange={() => toggleItem(item.id)}
                  className="w-4 h-4 rounded border-slate-300 dark:border-slate-600 dark:bg-slate-800 text-primary-blue focus:ring-primary-blue cursor-pointer accent-primary-blue"
                />
              </div>
              <div className="flex-1">
                <p className={`text-sm font-medium leading-snug ${item.done ? 'text-slate-400 dark:text-slate-500 line-through' : 'text-slate-700 dark:text-slate-200'}`}>
                  {item.text}
                </p>
                {!item.done && (
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${item.priority === 'High' ? 'bg-red-500' : item.priority === 'Medium' ? 'bg-yellow-500' : 'bg-slate-300 dark:bg-slate-600'}`}></span>
                    {item.priority} Priority
                  </p>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30 mt-auto">
        <button className="w-full py-2.5 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg text-slate-500 dark:text-slate-400 text-sm font-semibold hover:border-primary-blue hover:text-primary-blue dark:hover:border-blue-400 dark:hover:text-blue-400 transition-colors flex items-center justify-center gap-2">
          + Add New Action Item
        </button>
      </div>
    </div>
  );
};

export default ActionItems;
