'use client'

import React, { useState, useCallback, useEffect } from 'react'
import {
  Header,
  Sidebar,
  StatsGrid,
  AccountChart,
  PositionsTable,
  TradesTable,
  ConversationsList,
} from '@/components/features'
import AddModelModal from '@/components/features/AddModelModal'
import ApiProviderModal from '@/components/features/ApiProviderModal'
import SettingsModal from '@/components/features/SettingsModal'
import UpdateModal from '@/components/features/UpdateModal'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { useAppStore } from '@/store/useAppStore'
import { usePortfolio } from '@/hooks/usePortfolio'
import { initPerformanceMonitoring, logPerformanceReport } from '@/lib/performance'

export default function HomePage() {
  const { isAggregatedView } = useAppStore()
  const { portfolio, chartData, isLoading } = usePortfolio()
  
  // 模态对话框状态
  const [isAddModelOpen, setIsAddModelOpen] = useState(false)
  const [isApiProviderOpen, setIsApiProviderOpen] = useState(false)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isUpdateOpen, setIsUpdateOpen] = useState(false)
  
  // 刷新处理
  const handleRefresh = useCallback(() => {
    window.location.reload()
  }, [])
  
  // 初始化性能监控
  useEffect(() => {
    initPerformanceMonitoring()
    
    // 在页面加载完成后打印性能报告
    if (typeof window !== 'undefined') {
      window.addEventListener('load', () => {
        setTimeout(() => {
          logPerformanceReport()
        }, 3000)
      })
    }
  }, [])

  return (
    <div className="flex h-screen flex-col bg-gray-50 dark:bg-gray-950">
      <Header 
        onRefresh={handleRefresh}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenAddModel={() => setIsAddModelOpen(true)}
        onOpenApiProvider={() => setIsApiProviderOpen(true)}
        onOpenUpdate={() => setIsUpdateOpen(true)}
      />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="mx-auto max-w-7xl space-y-6">
            {/* 统计卡片网格 */}
            <StatsGrid portfolio={portfolio} isLoading={isLoading} />

            {/* 账户价值图表 */}
            <AccountChart 
              data={chartData} 
              type={isAggregatedView ? 'aggregated' : 'single'}
              isLoading={isLoading}
            />

            {/* 数据表格 - 仅在非聚合视图显示 */}
            {!isAggregatedView && (
              <Tabs defaultValue="positions" className="w-full">
                <TabsList>
                  <TabsTrigger value="positions">持仓</TabsTrigger>
                  <TabsTrigger value="trades">交易记录</TabsTrigger>
                  <TabsTrigger value="conversations">AI 对话</TabsTrigger>
                </TabsList>
                <TabsContent value="positions" className="mt-4">
                  <PositionsTable />
                </TabsContent>
                <TabsContent value="trades" className="mt-4">
                  <TradesTable />
                </TabsContent>
                <TabsContent value="conversations" className="mt-4">
                  <ConversationsList />
                </TabsContent>
              </Tabs>
            )}

            {/* 聚合视图提示 */}
            {isAggregatedView && (
              <div className="rounded-xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-gray-900">
                <p className="text-gray-600 dark:text-gray-400">
                  聚合视图模式下，仅显示所有模型的汇总数据和对比图表
                </p>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
                  选择单个模型以查看详细的持仓、交易记录和 AI 对话
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
      
      {/* 模态对话框 */}
      <AddModelModal 
        open={isAddModelOpen} 
        onOpenChange={setIsAddModelOpen} 
      />
      
      <ApiProviderModal 
        open={isApiProviderOpen} 
        onOpenChange={setIsApiProviderOpen} 
      />
      
      <SettingsModal 
        open={isSettingsOpen} 
        onOpenChange={setIsSettingsOpen} 
      />
      
      <UpdateModal 
        open={isUpdateOpen} 
        onOpenChange={setIsUpdateOpen}
        updateInfo={null} // TODO: 从 useUpdate hook 获取
      />
    </div>
  )
}
