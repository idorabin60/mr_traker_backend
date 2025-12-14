import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
    "inline-flex items-center justify-center white-space-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
    {
        variants: {
            variant: {
                default: "bg-white text-black hover:bg-zinc-200",
                destructive:
                    "bg-red-900 text-white hover:bg-red-800",
                outline:
                    "border border-zinc-800 bg-transparent hover:bg-zinc-900 text-white",
                secondary:
                    "bg-zinc-800 text-white hover:bg-zinc-700",
                ghost: "hover:bg-zinc-800 hover:text-white",
                link: "text-white underline-offset-4 hover:underline",
                whoop: "bg-[#FF0100] text-white hover:bg-[#D90100] font-bold uppercase tracking-widest text-xs shadow-[0_0_20px_rgba(255,1,0,0.3)] hover:shadow-[0_0_30px_rgba(255,1,0,0.5)] transition-all",
            },
            size: {
                default: "h-10 px-4 py-2",
                sm: "h-9 rounded-md px-3",
                lg: "h-11 rounded-md px-8",
                icon: "h-10 w-10",
            },
        },
        defaultVariants: {
            variant: "whoop",
            size: "default",
        },
    }
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, ...props }, ref) => {
        const Comp = asChild ? Slot : "button"
        return (
            <Comp
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
