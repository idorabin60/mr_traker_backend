"use client"

import React, { useState } from 'react';
import {
    Search, Bell, Settings, User, ChevronDown,
    RefreshCw, Filter, ArrowUpRight, MessageSquare,
    MoreHorizontal, Pin, Heart, Activity, Moon, Zap
} from 'lucide-react';
import {
    LineChart, Line, AreaChart, Area, BarChart, Bar,
    PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer
} from 'recharts';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from "@/components/ui/sheet";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

// --- MOCK DATA ---
const KPI_DATA = [
    { label: "Avg Recovery", value: "82%", trend: "+4%", status: "good", color: "text-emerald-400" },
    { label: "Avg Sleep", value: "7h 12m", trend: "-15m", status: "warning", color: "text-amber-400" },
    { label: "Avg Strain", value: "14.5", trend: "+1.2", status: "neutral", color: "text-blue-400" },
    { label: "At Risk", value: "3", trend: "High load", status: "danger", color: "text-red-400" },
];

const ATHLETES = [
    { id: 1, name: "Alex Rivera", role: "Forward", recovery: 94, sleep: "8h 30m", sleepScore: 98, strain: 12.4, hrv: 145, rhr: 42, status: "optimal", image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop" },
    { id: 2, name: "Sarah Chen", role: "Midfield", recovery: 32, sleep: "5h 45m", sleepScore: 45, strain: 18.2, hrv: 35, rhr: 58, status: "danger", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop" },
    { id: 3, name: "Marcus Johnson", role: "Defender", recovery: 68, sleep: "7h 10m", sleepScore: 78, strain: 15.5, hrv: 85, rhr: 48, status: "warning", image: "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150&h=150&fit=crop" },
    { id: 4, name: "Emily Davis", role: "Forward", recovery: 88, sleep: "7h 50m", sleepScore: 92, strain: 13.1, hrv: 110, rhr: 45, status: "optimal", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop" },
    { id: 5, name: "James Wilson", role: "Goalie", recovery: 45, sleep: "6h 15m", sleepScore: 60, strain: 10.2, hrv: 55, rhr: 52, status: "warning", image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop" },
    { id: 6, name: "Priya Patel", role: "Midfield", recovery: 91, sleep: "8h 05m", sleepScore: 95, strain: 16.8, hrv: 125, rhr: 44, status: "optimal", image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop" },
];

const ALERTS = [
    { id: 2, name: "Sarah Chen", type: "Low Recovery", value: "32%", action: "Check Load", priority: "high" },
    { id: 5, name: "James Wilson", type: "Sleep Debt", value: "-2h 30m", action: "Review Sched", priority: "medium" },
    { id: 3, name: "Marcus Johnson", type: "HRV Dip", value: "-15%", action: "Monitor", priority: "low" },
];

const RECOVERY_DATA = [
    { name: 'Optimal', value: 65, color: '#10b981' },
    { name: 'Strain', value: 25, color: '#f59e0b' },
    { name: 'Low', value: 10, color: '#ef4444' },
];

const WEEKLY_TREND_DATA = [
    { day: 'Mon', strain: 12, recovery: 85 },
    { day: 'Tue', strain: 14.5, recovery: 78 },
    { day: 'Wed', strain: 18, recovery: 45 },
    { day: 'Thu', strain: 10, recovery: 92 },
    { day: 'Fri', strain: 16, recovery: 68 },
    { day: 'Sat', strain: 19, recovery: 35 },
    { day: 'Sun', strain: 0, recovery: 95 },
];

// --- COMPONENTS ---

const StatusPill = ({ status, value }: any) => {
    const colors: Record<string, string> = {
        optimal: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        good: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        warning: "bg-amber-500/20 text-amber-400 border-amber-500/30",
        danger: "bg-red-500/20 text-red-400 border-red-500/30",
        neutral: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    };

    // Map numeric recovery to status if needed, or use string
    let statusKey = status;
    if (typeof value === 'number') {
        if (value >= 67) statusKey = 'optimal';
        else if (value >= 34) statusKey = 'warning';
        else statusKey = 'danger';
    }

    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${colors[statusKey] || colors.neutral} flex items-center gap-1.5`}>
            <span className={`w-1.5 h-1.5 rounded-full ${statusKey === 'optimal' || statusKey === 'good' ? 'bg-emerald-400' : statusKey === 'warning' ? 'bg-amber-400' : 'bg-red-400'}`}></span>
            {typeof value === 'number' ? `${value}%` : value || status}
        </span>
    );
};

const KPICard = ({ data }: any) => (
    <Card className="bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 transition-all duration-300">
        <CardContent className="p-5">
            <div className="flex justify-between items-start mb-2">
                <span className="text-neutral-400 text-sm font-medium">{data.label}</span>
                <Badge variant="outline" className={`bg-transparent border-0 ${data.color} px-0`}>
                    {data.trend}
                </Badge>
            </div>
            <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-neutral-50 tracking-tight">{data.value}</span>
            </div>
            <div className="mt-3 h-1 w-full bg-neutral-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${data.status === 'good' ? 'bg-emerald-500' : data.status === 'warning' ? 'bg-amber-500' : data.status === 'danger' ? 'bg-red-500' : 'bg-blue-500'}`} style={{ width: '70%' }}></div>
            </div>
        </CardContent>
    </Card>
);

const AthleteCard = ({ athlete, onSelect }: any) => (
    <Card
        className="bg-neutral-900 border-neutral-800 hover:border-neutral-700 hover:bg-neutral-900/80 transition-all duration-300 cursor-pointer group"
        onClick={() => onSelect(athlete)}
    >
        <CardContent className="p-5">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10 ring-2 ring-neutral-800 group-hover:ring-neutral-700 transition-all">
                        <AvatarImage src={athlete.image} />
                        <AvatarFallback>{athlete.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                        <h3 className="font-medium text-neutral-50 leading-none">{athlete.name}</h3>
                        <span className="text-xs text-neutral-400 mt-1 block">{athlete.role}</span>
                    </div>
                </div>
                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-neutral-400 hover:text-white">
                        <MoreHorizontal className="w-4 h-4" />
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="flex flex-col gap-1 p-2 rounded bg-neutral-950/50">
                    <span className="text-[10px] text-neutral-500 uppercase font-semibold">Recovery</span>
                    <StatusPill value={athlete.recovery} />
                </div>
                <div className="flex flex-col gap-1 p-2 rounded bg-neutral-950/50">
                    <span className="text-[10px] text-neutral-500 uppercase font-semibold">Strain</span>
                    <span className="text-sm font-semibold text-blue-400">{athlete.strain}</span>
                </div>
                <div className="flex flex-col gap-1 p-2 rounded bg-neutral-950/50">
                    <span className="text-[10px] text-neutral-500 uppercase font-semibold">Sleep</span>
                    <span className="text-sm font-semibold text-neutral-200">{athlete.sleep}</span>
                </div>
            </div>

            <div className="flex items-center justify-between text-xs text-neutral-500 border-t border-neutral-800 pt-3">
                <div className="flex gap-3">
                    <span className="flex items-center gap-1"><Heart className="w-3 h-3" /> {athlete.rhr} RHR</span>
                    <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> {athlete.hrv} ms</span>
                </div>
                <div className="h-4 w-12">
                    {/* Mini sparkline placeholder */}
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={WEEKLY_TREND_DATA}>
                            <Line type="monotone" dataKey="recovery" stroke={athlete.recovery > 66 ? "#10b981" : "#ef4444"} strokeWidth={2} dot={false} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </CardContent>
    </Card>
);

const AthleteDrawer = ({ athlete, isOpen, onClose }: any) => (
    <Sheet open={isOpen} onOpenChange={onClose}>
        <SheetContent className="bg-neutral-950 border-l-neutral-800 text-neutral-50 w-full sm:max-w-md overflow-y-auto">
            <SheetHeader className="mb-6">
                <div className="flex items-center gap-4">
                    <Avatar className="h-16 w-16 ring-4 ring-neutral-900">
                        <AvatarImage src={athlete?.image} />
                        <AvatarFallback>{athlete?.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                        <SheetTitle className="text-2xl font-bold text-neutral-50">{athlete?.name}</SheetTitle>
                        <SheetDescription className="text-neutral-400">{athlete?.role} • {athlete?.status === 'optimal' ? 'Ready to Perform' : 'Needs Recovery'}</SheetDescription>
                    </div>
                </div>
            </SheetHeader>

            {athlete && (
                <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-3">
                        <Card className="bg-neutral-900 border-neutral-800">
                            <CardContent className="p-4 flex flex-col items-center justify-center">
                                <span className="text-neutral-400 text-xs uppercase mb-1">Recovery</span>
                                <span className={`text-4xl font-bold ${athlete.recovery > 66 ? 'text-emerald-400' : 'text-red-400'}`}>{athlete.recovery}%</span>
                            </CardContent>
                        </Card>
                        <Card className="bg-neutral-900 border-neutral-800">
                            <CardContent className="p-4 flex flex-col items-center justify-center">
                                <span className="text-neutral-400 text-xs uppercase mb-1">Strain</span>
                                <span className="text-4xl font-bold text-blue-400">{athlete.strain}</span>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="space-y-2">
                        <h4 className="text-sm font-semibold text-neutral-300">Last 7 Days</h4>
                        <div className="h-40 w-full bg-neutral-900/50 rounded-lg border border-neutral-800 p-2">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={WEEKLY_TREND_DATA}>
                                    <defs>
                                        <linearGradient id="colorRecovery" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorStrain" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                    <XAxis dataKey="day" stroke="#525252" fontSize={10} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#525252" fontSize={10} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', borderRadius: '8px' }}
                                        itemStyle={{ color: '#d4d4d4' }}
                                    />
                                    <Area type="monotone" dataKey="recovery" stroke="#10b981" fillOpacity={1} fill="url(#colorRecovery)" strokeWidth={2} />
                                    <Area type="monotone" dataKey="strain" stroke="#3b82f6" fillOpacity={1} fill="url(#colorStrain)" strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <h4 className="text-sm font-semibold text-neutral-300">Coach Notes</h4>
                            <Button variant="ghost" size="sm" className="h-6 text-xs text-neutral-500">History</Button>
                        </div>
                        <textarea
                            className="w-full h-24 bg-neutral-900 border border-neutral-800 rounded-lg p-3 text-sm text-neutral-200 placeholder:text-neutral-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 resize-none"
                            placeholder="Add a note about today's session..."
                        />
                        <div className="flex justify-end">
                            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white">Save Note</Button>
                        </div>
                    </div>

                    <div className="pt-4 border-t border-neutral-800 flex gap-2">
                        <Button variant="outline" className="flex-1 border-neutral-700 hover:bg-neutral-800 text-neutral-300">
                            <MessageSquare className="w-4 h-4 mr-2" /> Message
                        </Button>
                        <Button variant="outline" className="flex-1 border-neutral-700 hover:bg-neutral-800 text-neutral-300">
                            <Pin className="w-4 h-4 mr-2" /> Pin
                        </Button>
                    </div>
                </div>
            )}
        </SheetContent>
    </Sheet>
);

export default function TrainerDashboard() {
    const [selectedAthlete, setSelectedAthlete] = useState(null);
    const [athleteFilter, setAthleteFilter] = useState("all");

    const filteredAthletes = ATHLETES.filter(a => {
        if (athleteFilter === "all") return true;
        if (athleteFilter === "risk") return a.status === "danger" || a.status === "warning";
        return true;
    });

    return (
        <div className="min-h-screen pb-10">
            {/* Sticky Header */}
            <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-neutral-950/80 border-b border-neutral-800">
                <div className="container mx-auto max-w-7xl px-4 h-16 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center">
                                <Activity className="text-neutral-950 w-5 h-5" />
                            </div>
                            <span className="text-lg font-bold tracking-tight">Mr_Traker</span>
                        </div>
                        <nav className="hidden md:flex items-center gap-1">
                            <Button variant="ghost" className="text-neutral-400 hover:text-white hover:bg-white/5">Dashboard</Button>
                            <Button variant="ghost" className="text-neutral-400 hover:text-white hover:bg-white/5">Team</Button>
                            <Button variant="ghost" className="text-neutral-400 hover:text-white hover:bg-white/5">Reports</Button>
                        </nav>
                    </div>

                    <div className="flex-1 max-w-md hidden md:block relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
                        <Input
                            placeholder="Search athlete..."
                            className="bg-neutral-900/50 border-neutral-800 pl-9 text-neutral-200 focus-visible:ring-emerald-500/50 placeholder:text-neutral-600"
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        <Button variant="ghost" size="icon" className="text-neutral-400 hover:text-white hover:bg-white/5 relative">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-2 right-2 w-2 h-2 bg-emerald-500 rounded-full"></span>
                        </Button>
                        <Avatar className="h-8 w-8 ring-2 ring-neutral-800 cursor-pointer">
                            <AvatarImage src="https://github.com/shadcn.png" />
                            <AvatarFallback>CO</AvatarFallback>
                        </Avatar>
                    </div>
                </div>
            </header>

            <main className="container mx-auto max-w-7xl px-4 pt-6 space-y-8">
                {/* Top Controls */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div className="flex items-center gap-2 text-sm text-neutral-400 bg-neutral-900/50 rounded-lg p-1 pr-3 border border-neutral-800">
                        <Tabs defaultValue="today" className="h-8">
                            <TabsList className="h-full bg-transparent p-0 gap-1">
                                <TabsTrigger value="today" className="h-7 rounded-md px-3 text-xs data-[state=active]:bg-neutral-800 data-[state=active]:text-white text-neutral-500">Today</TabsTrigger>
                                <TabsTrigger value="7d" className="h-7 rounded-md px-3 text-xs data-[state=active]:bg-neutral-800 data-[state=active]:text-white text-neutral-500">7D</TabsTrigger>
                                <TabsTrigger value="30d" className="h-7 rounded-md px-3 text-xs data-[state=active]:bg-neutral-800 data-[state=active]:text-white text-neutral-500">30D</TabsTrigger>
                            </TabsList>
                        </Tabs>
                        <Separator orientation="vertical" className="h-4 bg-neutral-800" />
                        <span className="flex items-center gap-1.5 ml-1 text-xs">
                            <RefreshCw className="w-3 h-3" /> Last synced 2m ago
                        </span>
                    </div>

                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                        Export Report
                    </Button>
                </div>

                {/* Section 1: KPI Overview */}
                <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {KPI_DATA.map((kpi, idx) => (
                        <KPICard key={idx} data={kpi} />
                    ))}
                </section>

                {/* Section 2: Priority Queue */}
                <section>
                    <div className="flex items-center gap-3 mb-4">
                        <h2 className="text-lg font-semibold text-neutral-200">Priority Attention</h2>
                        <Badge variant="secondary" className="bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20">3 Critical</Badge>
                    </div>
                    <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl overflow-hidden backdrop-blur-sm">
                        <div className="divide-y divide-neutral-800/50">
                            {ALERTS.map((alert, idx) => {
                                const athlete = ATHLETES.find(a => a.id === alert.id);
                                return (
                                    <div key={idx} className="p-4 flex flex-col sm:flex-row items-center justify-between gap-4 hover:bg-white/5 transition-colors group">
                                        <div className="flex items-center gap-4 w-full sm:w-auto">
                                            <Avatar className="h-10 w-10 ring-2 ring-neutral-800">
                                                <AvatarImage src={athlete?.image} />
                                                <AvatarFallback>{athlete?.name.substring(0, 2)}</AvatarFallback>
                                            </Avatar>
                                            <div>
                                                <p className="font-medium text-neutral-50">{athlete?.name}</p>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <Badge variant="outline" className="border-red-500/30 text-red-400 bg-red-500/10 text-[10px] uppercase font-bold tracking-wider">
                                                        {alert.type}
                                                    </Badge>
                                                    <span className="text-sm text-neutral-400">{alert.value} vs baseline</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
                                            <span className="text-xs text-neutral-500 italic hidden sm:block">Requires Check-in</span>
                                            <Button size="sm" variant="outline" className="border-neutral-700 text-neutral-300 hover:text-white hover:bg-neutral-800">
                                                {alert.action}
                                            </Button>
                                            <Button size="sm" className="bg-neutral-800 hover:bg-neutral-700 text-white">
                                                Message
                                            </Button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </section>

                {/* Section 3: Dashboards */}
                <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Recovery Distribution */}
                    <Card className="bg-neutral-900 border-neutral-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg text-neutral-200">Team Recovery</CardTitle>
                            <CardDescription className="text-neutral-500">Distribution of today's recovery scores</CardDescription>
                        </CardHeader>
                        <CardContent className="flex items-center justify-center h-64 relative">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={RECOVERY_DATA}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {RECOVERY_DATA.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', borderRadius: '8px' }}
                                        itemStyle={{ color: '#d4d4d4' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                <span className="text-3xl font-bold text-neutral-50">82%</span>
                                <span className="text-xs text-neutral-500 uppercase tracking-wide">Avg</span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Strain vs Recovery Trend */}
                    <Card className="bg-neutral-900 border-neutral-800">
                        <CardHeader className="pb-2 flex flex-row items-center justify-between">
                            <div>
                                <CardTitle className="text-lg text-neutral-200">Load vs Recovery</CardTitle>
                                <CardDescription className="text-neutral-500">7-day team average trend</CardDescription>
                            </div>
                            <div className="flex gap-2">
                                <div className="flex items-center gap-1.5 text-xs text-neutral-400">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500"></div> Rec
                                </div>
                                <div className="flex items-center gap-1.5 text-xs text-neutral-400">
                                    <div className="w-2 h-2 rounded-full bg-blue-500"></div> Strain
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="h-64 pt-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={WEEKLY_TREND_DATA}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                    <XAxis dataKey="day" stroke="#525252" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis yAxisId="left" stroke="#525252" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis yAxisId="right" orientation="right" stroke="#525252" fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', borderRadius: '8px' }}
                                    />
                                    <Line yAxisId="left" type="monotone" dataKey="recovery" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: "#10b981" }} activeDot={{ r: 6 }} />
                                    <Line yAxisId="right" type="monotone" dataKey="strain" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: "#3b82f6" }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Sleep Architecture */}
                    <Card className="bg-neutral-900 border-neutral-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg text-neutral-200">Sleep Performance</CardTitle>
                            <CardDescription className="text-neutral-500">Average sleep stages (Last 7D)</CardDescription>
                        </CardHeader>
                        <CardContent className="h-64 pt-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={[
                                    { day: 'Mon', deep: 1.5, light: 4, rem: 1.8, awake: 0.5 },
                                    { day: 'Tue', deep: 1.2, light: 3.8, rem: 1.5, awake: 0.8 },
                                    { day: 'Wed', deep: 1.8, light: 4.2, rem: 2.0, awake: 0.3 },
                                    { day: 'Thu', deep: 1.4, light: 3.9, rem: 1.7, awake: 0.4 },
                                    { day: 'Fri', deep: 1.1, light: 3.5, rem: 1.4, awake: 1.0 },
                                    { day: 'Sat', deep: 2.0, light: 4.5, rem: 2.2, awake: 0.2 },
                                    { day: 'Sun', deep: 1.9, light: 4.3, rem: 2.1, awake: 0.3 },
                                ]}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                                    <XAxis dataKey="day" stroke="#525252" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#525252" fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', borderRadius: '8px' }}
                                        cursor={{ fill: '#262626', opacity: 0.4 }}
                                    />
                                    <Bar dataKey="deep" stackId="a" fill="#8b5cf6" radius={[0, 0, 0, 0]} />
                                    <Bar dataKey="rem" stackId="a" fill="#a78bfa" radius={[0, 0, 0, 0]} />
                                    <Bar dataKey="light" stackId="a" fill="#c4b5fd" radius={[0, 0, 0, 0]} />
                                    <Bar dataKey="awake" stackId="a" fill="#525252" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Consistency Heatmap */}
                    <Card className="bg-neutral-900 border-neutral-800">
                        <CardHeader className="pb-2 flex flex-row items-center justify-between">
                            <div>
                                <CardTitle className="text-lg text-neutral-200">Consistency</CardTitle>
                                <CardDescription className="text-neutral-500">Training adherence (Last 4 Weeks)</CardDescription>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-neutral-500">Less</span>
                                <div className="flex gap-1">
                                    <div className="w-2 h-2 rounded-sm bg-neutral-800"></div>
                                    <div className="w-2 h-2 rounded-sm bg-emerald-900"></div>
                                    <div className="w-2 h-2 rounded-sm bg-emerald-600"></div>
                                    <div className="w-2 h-2 rounded-sm bg-emerald-400"></div>
                                </div>
                                <span className="text-xs text-neutral-500">More</span>
                            </div>
                        </CardHeader>
                        <CardContent className="h-64 flex items-center justify-center p-6">
                            <div className="grid grid-cols-7 gap-2 w-full max-w-sm">
                                {Array.from({ length: 28 }).map((_, i) => {
                                    const opacity = Math.random() > 0.8 ? 'bg-neutral-800' :
                                        Math.random() > 0.6 ? 'bg-emerald-900' :
                                            Math.random() > 0.3 ? 'bg-emerald-600' : 'bg-emerald-400';
                                    return (
                                        <div
                                            key={i}
                                            className={`aspect-square rounded-sm ${opacity} hover:opacity-80 transition-opacity cursor-pointer`}
                                            title={`Day ${i + 1}`}
                                        />
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>
                </section>

                {/* Section 4: Athletes Grid */}
                <section>
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                        <div className="flex items-center gap-2">
                            <h2 className="text-xl font-bold text-neutral-100">Roster</h2>
                            <Badge variant="outline" className="border-neutral-700 text-neutral-400">{ATHLETES.length}</Badge>
                        </div>

                        <div className="flex items-center gap-3 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0 no-scrollbar">
                            <div className="flex bg-neutral-900 border border-neutral-800 rounded-lg p-1">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className={`h-7 px-3 text-xs ${athleteFilter === 'all' ? 'bg-neutral-800 text-white' : 'text-neutral-400 hover:text-white'}`}
                                    onClick={() => setAthleteFilter('all')}
                                >
                                    All
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className={`h-7 px-3 text-xs ${athleteFilter === 'risk' ? 'bg-neutral-800 text-white' : 'text-neutral-400 hover:text-white'}`}
                                    onClick={() => setAthleteFilter('risk')}
                                >
                                    At Risk
                                </Button>
                            </div>

                            <Select defaultValue="recovery_asc">
                                <SelectTrigger className="w-[140px] h-9 bg-neutral-900 border-neutral-800 text-neutral-300 text-xs">
                                    <SelectValue placeholder="Sort by" />
                                </SelectTrigger>
                                <SelectContent className="bg-neutral-900 border-neutral-800 text-neutral-300">
                                    <SelectItem value="recovery_asc">Recovery (Low)</SelectItem>
                                    <SelectItem value="strain_desc">Strain (High)</SelectItem>
                                    <SelectItem value="sleep_asc">Sleep (Low)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredAthletes.map(athlete => (
                            <AthleteCard
                                key={athlete.id}
                                athlete={athlete}
                                onSelect={setSelectedAthlete}
                            />
                        ))}

                        {/* Invite Card */}
                        <Card className="bg-neutral-900/30 border-neutral-800 border-dashed hover:bg-neutral-900/50 hover:border-neutral-700 transition-all cursor-pointer flex items-center justify-center min-h-[200px] group">
                            <div className="flex flex-col items-center gap-3 text-neutral-500 group-hover:text-neutral-400 transition-colors">
                                <div className="w-12 h-12 rounded-full bg-neutral-800/50 flex items-center justify-center group-hover:bg-neutral-800">
                                    <User className="w-6 h-6" />
                                </div>
                                <span className="font-medium text-sm">Add New Athlete</span>
                            </div>
                        </Card>
                    </div>
                </section>
            </main>

            {/* Drawers & Modals */}
            <AthleteDrawer
                athlete={selectedAthlete}
                isOpen={!!selectedAthlete}
                onClose={() => setSelectedAthlete(null)}
            />
        </div>
    );
}
