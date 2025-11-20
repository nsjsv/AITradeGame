'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { Loader2 } from 'lucide-react'
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
      <div className="flex h-screen flex-col bg-background text-foreground">
        <Header 
          onRefresh={handleRefresh}
          onOpenSettings={() => openModal('settings')}
          onOpenAddModel={() => openModal('addModel')}
          onOpenApiProvider={() => openModal('apiProvider')}
          onOpenUpdate={() => openModal('update')}
        />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-background p-4 md:p-6">
            <div className="mx-auto flex max-w-7xl flex-col gap-4">
              {isRefreshing && (
                <div className="inline-flex items-center gap-2 rounded-full border border-border/80 bg-card/80 px-4 py-1 text-xs text-muted-foreground shadow-soft backdrop-blur">
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-foreground/70" />
                  <span>正在同步最新账户数据...</span>
                </div>
              )}
              <div
                className={cn(
                  'space-y-6 transition-all duration-300',
                  isRefreshing && 'blur-[1px] opacity-70'
                )}
              >
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
                    <PositionsTable
                      portfolio={portfolio}
                      isLoading={isLoading}
                    />
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
                  <div className="rounded-2xl border border-border bg-card/80 p-8 text-center shadow-soft">
                    <p className="text-base text-foreground/80">
                      聚合视图模式下，仅显示所有模型的汇总数据和对比图表
                    </p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      选择单个模型以查看详细的持仓、交易记录和 AI 对话
                    </p>
                  </div>
                )}
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
