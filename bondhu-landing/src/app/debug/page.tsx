"use client"

import { useEffect, useState } from "react"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function DatabaseTestPage() {
    const [results, setResults] = useState<any[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const supabase = createClient()

    const runTests = async () => {
        setIsLoading(true)
        const testResults: any[] = []

        try {
            // Test 1: Auth user
            const { data: { user }, error: userError } = await supabase.auth.getUser()
            testResults.push({
                test: 'Authentication',
                status: userError ? 'FAILED' : 'PASSED',
                result: userError ? userError : `User ID: ${user?.id}`,
                details: user
            })

            // Test 2: Database connection
            const { data: connTest, error: connError } = await supabase
                .from('profiles')
                .select('count')
                .limit(1)

            testResults.push({
                test: 'Database Connection',
                status: connError ? 'FAILED' : 'PASSED',
                result: connError ? connError.message : 'Connection successful',
                details: connError
            })

            // Test 3: Profile table structure
            const { data: tableTest, error: tableError } = await supabase
                .from('profiles')
                .select('*')
                .limit(1)

            testResults.push({
                test: 'Profiles Table',
                status: tableError ? 'FAILED' : 'PASSED',
                result: tableError ? tableError.message : 'Table accessible',
                details: tableError
            })

            // Test 4: User profile check
            if (user) {
                const { data: profileData, error: profileError } = await supabase
                    .from('profiles')
                    .select('*')
                    .eq('id', user.id)
                    .single()

                testResults.push({
                    test: 'User Profile',
                    status: profileError && profileError.code !== 'PGRST116' ? 'FAILED' : 'PASSED',
                    result: profileError?.code === 'PGRST116'
                        ? 'Profile not found (normal for new users)'
                        : profileError
                            ? profileError.message
                            : 'Profile exists',
                    details: profileData || profileError
                })
            }

            // Test 5: Insert test (if user exists)
            if (user && !testResults.find(t => t.test === 'User Profile' && t.status === 'FAILED')) {
                const testData = {
                    id: user.id,
                    full_name: 'Test User',
                    personality_data: { test: true },
                    onboarding_completed: false,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                }

                const { data: insertData, error: insertError } = await supabase
                    .from('profiles')
                    .upsert(testData, { onConflict: 'id' })
                    .select()

                testResults.push({
                    test: 'Profile Insert/Update',
                    status: insertError ? 'FAILED' : 'PASSED',
                    result: insertError ? insertError.message : 'Insert/Update successful',
                    details: insertError || insertData
                })
            }

        } catch (error: any) {
            testResults.push({
                test: 'General Error',
                status: 'FAILED',
                result: error.message,
                details: error
            })
        }

        setResults(testResults)
        setIsLoading(false)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20 p-4">
            <div className="max-w-4xl mx-auto pt-8">
                <Card>
                    <CardHeader>
                        <CardTitle>Database Connection Test</CardTitle>
                        <p className="text-muted-foreground">
                            This page tests the Supabase connection and profiles table setup
                        </p>
                    </CardHeader>
                    <CardContent>
                        <Button
                            onClick={runTests}
                            disabled={isLoading}
                            className="mb-6"
                        >
                            {isLoading ? 'Running Tests...' : 'Run Database Tests'}
                        </Button>

                        {results.length > 0 && (
                            <div className="space-y-4">
                                {results.map((result, index) => (
                                    <Card key={index} className="p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <h3 className="font-semibold">{result.test}</h3>
                                            <span className={`px-2 py-1 rounded text-sm ${result.status === 'PASSED'
                                                    ? 'bg-green-100 text-green-800'
                                                    : 'bg-red-100 text-red-800'
                                                }`}>
                                                {result.status}
                                            </span>
                                        </div>
                                        <p className="text-sm text-muted-foreground mb-2">
                                            {result.result}
                                        </p>
                                        {result.details && (
                                            <details className="text-xs">
                                                <summary className="cursor-pointer">View Details</summary>
                                                <pre className="mt-2 p-2 bg-muted rounded overflow-auto">
                                                    {JSON.stringify(result.details, null, 2)}
                                                </pre>
                                            </details>
                                        )}
                                    </Card>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}