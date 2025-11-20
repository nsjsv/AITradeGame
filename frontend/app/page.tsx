'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Header,
  Sidebar,
  StatsGrid,
  AccountChart,
  PositionsTable,
  TradesTable,
  ConversationsList,
  PageLoadingOverlay,
} from '@/components/features'
import AddModelModal from '@/components/features/AddModelModal'
import ApiProviderModal from '@/components/features/ApiProviderModal'
import SettingsModal from '@/components/features/SettingsModal'
import UpdateModal from '@/components/features/UpdateModal'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { useAppStore } from '@/store/useAppStore'
import { usePortfolio } from '@/hooks/usePortfolio'
import { initPerformanceMonitoring, logPerformanceReport } from '@/lib/performance'
import { cn } from '@/lib/utils'

export default function HomePage() {
  const isAggregatedView = useAppStore((state) => state.isAggregatedView)
  const isRefreshing = useAppStore((state) => state.isRefreshing)
  const { portfolio, chartData, isLoading, loadPortfolio } = usePortfolio()
  
  type ModalType = 'addModel' | 'apiProvider' | 'settings' | 'update'
  const [activeModal, setActiveModal] = useState<ModalType | null>(null)
  const handleModalOpenChange = useCallback(
    (modal: ModalType) => (open: boolean) => {
      setActiveModal(open ? modal : null)
    },
    []
  )
  const openModal = useCallback((modal: ModalType) => setActiveModal(modal), [])
  
  // 刷新处理
  const handleRefresh = useCallback(() => {
    void loadPortfolio()
  }, [loadPortfolio])
  
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
    <>
      <PageLoadingOverlay show={isLoading} message="正在初始化界面，请稍候…" />
      <div className="flex h-screen w-full bg-background text-foreground">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header
            onRefresh={handleRefresh}
            onOpenSettings={() => openModal('settings')}
            onOpenAddModel={() => openModal('addModel')}
            onOpenApiProvider={() => openModal('apiProvider')}
            onOpenUpdate={() => openModal('update')}
          />
          <main className="flex-1 overflow-y-auto p-4 md:p-8 lg:p-10">
            <div className="mx-auto max-w-6xl space-y-8">
              {/* 页面标题区域 */}
              <div className="flex items-center justify-between">
                 <div className="space-y-1">
                    <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
                    <p className="text-sm text-muted-foreground">
                      {isAggregatedView ? '全平台资产概览' : '模型详细数据监控'}
                    </p>
                 </div>
                 {isRefreshing && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>同步中...</span>
                  </div>
                )}
              </div>

              <div
                className={cn(
                  'space-y-8 transition-all duration-300',
                  isRefreshing && 'opacity-60'
                )}
              >
                {/* 统计卡片网格 */}
                <StatsGrid portfolio={portfolio} isLoading={isLoading} />

                {/* 账户价值图表 */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                  className="rounded-lg border bg-card text-card-foreground shadow-sm"
                >
                  <div className="p-6 pb-0">
                    <h3 className="font-semibold leading-none tracking-tight">资产趋势</h3>
                    <p className="text-sm text-muted-foreground mt-1">过去 24 小时净值变化</p>
                  </div>
                  <div className="p-6 pt-4">
                    <AccountChart
                      data={chartData}
                      type={isAggregatedView ? 'aggregated' : 'single'}
                      isLoading={isLoading}
                    />
                  </div>
                </motion.div>

                {/* 视图切换区域 */}
                <AnimatePresence mode="wait">
                  {!isAggregatedView ? (
                    <motion.div
                      key="detail-view"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Tabs defaultValue="positions" className="w-full space-y-4">
                        <TabsList className="bg-muted/50 p-1">
                          <TabsTrigger value="positions" className="text-xs">持仓管理</TabsTrigger>
                          <TabsTrigger value="trades" className="text-xs">交易历史</TabsTrigger>
                          <TabsTrigger value="conversations" className="text-xs">AI 决策日志</TabsTrigger>
                        </TabsList>
                        <TabsContent value="positions" className="space-y-4">
                          <PositionsTable
                            portfolio={portfolio}
                            isLoading={isLoading}
                          />
                        </TabsContent>
                        <TabsContent value="trades" className="space-y-4">
                          <TradesTable />
                        </TabsContent>
                        <TabsContent value="conversations" className="space-y-4">
                          <ConversationsList />
                        </TabsContent>
                      </Tabs>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="aggregated-view"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 1.05 }}
                      transition={{ duration: 0.3 }}
                      className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center"
                    >
                      <div className="rounded-full bg-muted/50 p-3">
                         <Loader2 className="h-6 w-6 text-muted-foreground" />
                      </div>
                      <h3 className="mt-4 text-lg font-semibold">聚合视图模式</h3>
                      <p className="mt-2 text-sm text-muted-foreground max-w-sm">
                        当前显示所有模型的汇总数据。如需查看特定模型的详细持仓和交易记录，请在左侧侧边栏选择对应模型。
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </main>
        </div>
        
        {/* 模态对话框 */}
        <AddModelModal
          open={activeModal === 'addModel'}
          onOpenChange={handleModalOpenChange('addModel')}
        />
        
        <ApiProviderModal
          open={activeModal === 'apiProvider'}
          onOpenChange={handleModalOpenChange('apiProvider')}
        />
        
        <SettingsModal
          open={activeModal === 'settings'}
          onOpenChange={handleModalOpenChange('settings')}
        />
        
        <UpdateModal
          open={activeModal === 'update'}
          onOpenChange={handleModalOpenChange('update')}
          updateInfo={null} // TODO: 从 useUpdate hook 获取
        />
      </div>
    </>
  )
}
