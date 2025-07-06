# ❌ Workflow Execution Failed

## 🚨 Error Details
- **Failed Agent**: SecurityReviewer
- **Agent Type**: LlmAgent
- **Agent Model**: gemini-2.5-flash
- **Error Type**: ClientError
- **Error Category**: rate_limit
- **Timestamp**: 2025-07-06 14:59:34

## 📝 Error Message
```
429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_input_token_count', 'quotaId': 'GenerateContentInputTokensPerModelPerMinute-FreeTier', 'quotaDimensions': {'model': 'gemini-2.5-flash', 'location': 'global'}, 'quotaValue': '250000'}]}, {'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '26s'}]}}
```

## ✅ Successfully Completed Agents
1. **RequirementAnalyzer** - ✅ Completed with Output
2. **ArchitecturalDesigner** - ✅ Completed with Output
3. **CodeGenerator** - ✅ Completed with Output
4. **QualityReviewer** - ✅ Completed with Output
5. **PerformanceReviewer** - ✅ Completed with Output
6. **SecurityReviewer** - ✅ Completed with Output

## 📊 Partial Execution Statistics
- **Total Agents in Workflow**: 10
- **Agents Executed**: 6
- **Agents with Outputs**: 6
- **Success Rate**: 100.0%

## 💾 Available Outputs
You have the following partial results available:
- **RequirementAnalyzer**: See `*_requirementanalyzer.md`
- **ArchitecturalDesigner**: See `*_architecturaldesigner.md`
- **CodeGenerator**: See `*_codegenerator.md`
- **QualityReviewer**: See `*_qualityreviewer.md`
- **PerformanceReviewer**: See `*_performancereviewer.md`
- **SecurityReviewer**: See `*_securityreviewer.md`

## 🔧 Troubleshooting
- Check the failed agent configuration
- Verify API quotas and connectivity
- Review agent-specific logs above
- Consider running from the last successful checkpoint

## 🔄 Recovery Options
1. **Partial Results**: Use the outputs from successful agents
2. **Restart from Checkpoint**: Modify workflow to start from last successful agent
3. **Debug Mode**: Run individual agents to isolate the issue

---
*Error report generated at 2025-07-06 14:59:34*
