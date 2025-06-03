// === ROSETTA STONE AGENT - INTERACTIVE MAGIC === //

class RosettaStoneUI {
    constructor() {
        this.currentFramework = 'smolagents';
        this.isProcessing = false;
        this.messageHistory = [];
        this.apiBaseUrl = '';
        
        // Initialize the interface
        this.initializeEventListeners();
        this.setupFrameworkSwitching();
        this.setupStoneInteractions();
        this.setupChatFunctionality();
        this.initializeSession(); 
        console.log('🏺 Rosetta Stone Agent UI Initialized');
    }

    initializeEventListeners() {
        // Framework pillar clicks
        document.querySelectorAll('.pillar').forEach(pillar => {
            pillar.addEventListener('click', (e) => {
                const framework = e.currentTarget.dataset.framework;
                this.switchFramework(framework);
            });
        });

        // Send message functionality
        const sendButton = document.getElementById('sendMessage');
        const messageInput = document.getElementById('messageInput');
        
        sendButton.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Clear chat functionality
        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });

        // Stone clicking for awakening
        document.getElementById('rosettaStone').addEventListener('click', () => {
            this.awakeneStone();
        });
    }

    setupFrameworkSwitching() {
        // Set initial framework display
        this.updateFrameworkDisplay();
    }

    async switchFramework(framework) {
        if (this.isProcessing) return;
        
        this.currentFramework = framework;
        
        // Update active pillar
        document.querySelectorAll('.pillar').forEach(p => p.classList.remove('active'));
        document.querySelector(`[data-framework="${framework}"]`).classList.add('active');
        
        // Update stone display
        this.updateFrameworkDisplay();
        
        // Call real backend to switch framework
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/switch_framework`, {

                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    framework: framework
                })
            });
    
            const data = await response.json();
            
            if (data.success) {
                this.addSystemMessage(`🔄 **Framework Awakened: ${framework.toUpperCase()}**\n\n${this.getFrameworkDescription(framework)}\n\n*The ancient stone channels new pathways of wisdom through the real Python backend...*`);
            }
        } catch (error) {
            console.error('Error switching framework:', error);
            this.addSystemMessage(`🔄 **Framework Switched: ${framework.toUpperCase()}**\n\n${this.getFrameworkDescription(framework)}\n\n*Framework changed locally (backend connection needed for full effect)*`);
        }
        
        // Animate stone transformation
        this.animateFrameworkSwitch();
        
        console.log(`🔄 Switched to framework: ${framework}`);
    }
    async initializeSession() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/start_session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'web_ui_user'
                })
            });
    
            const data = await response.json();
            if (data.success) {
                console.log('✅ Session started with real Python backend');
                this.addSystemMessage(`🔗 **Connected to Real Rosetta Stone Agent**\n\nThe ancient stone awakens with true consciousness!\nSession ID: ${data.session_info.session_id}\nFramework: ${this.currentFramework.toUpperCase()}\n\n*Now you speak to the real Rosetta Stone...*`);
            }
        } catch (error) {
            console.error('Failed to start session:', error);
            this.addSystemMessage(`⚠️ **Connection Warning**\n\nUsing simulated responses. To connect to the real agent, ensure the Python backend is running at http://localhost:8080`);
        }
    }
    updateFrameworkDisplay() {
        const indicator = document.getElementById('frameworkIndicator');
        const frameworkName = indicator.querySelector('.framework-name');
        
        frameworkName.textContent = this.currentFramework.toUpperCase();
        
        // Update colors based on framework
        const colors = {
            smolagents: '#3b82f6',    // Electric blue
            llamaindex: '#8b5cf6',   // Purple
            langgraph: '#10b981'     // Emerald
        };
        
        const powerLevel = indicator.querySelector('.power-level');
        powerLevel.style.background = `linear-gradient(90deg, ${colors[this.currentFramework]}, ${colors[this.currentFramework]}88)`;
        
        // Update stone glow
        const stoneGlow = document.getElementById('stoneGlow');
        stoneGlow.style.background = `radial-gradient(circle, ${colors[this.currentFramework]}40 0%, transparent 70%)`;
    }

    getFrameworkDescription(framework) {
        const descriptions = {
            smolagents: "SmolAgents Framework\n• Lightning-fast processing\n• Efficient tool orchestration\n• Minimal computational overhead\n• Perfect for quick queries and real-time responses",
            llamaindex: "LlamaIndex Framework\n• Deep knowledge retrieval\n• Advanced vector search\n• Semantic understanding\n• Ideal for complex research and knowledge synthesis",
            langgraph: "LangGraph Framework\n• Multi-step reasoning chains\n• Advanced state management\n• Complex workflow orchestration\n• Best for intricate problem-solving and analysis"
        };
        return descriptions[framework] || "";
    }

    setupStoneInteractions() {
        const stone = document.getElementById('rosettaStone');
        const stoneGlow = document.getElementById('stoneGlow');
        
        // Add hover effects
        stone.addEventListener('mouseenter', () => {
            stoneGlow.style.opacity = '0.6';
            this.animateScripts();
        });
        
        stone.addEventListener('mouseleave', () => {
            stoneGlow.style.opacity = '0.1';
        });
    }

    awakeneStone() {
        const stone = document.getElementById('rosettaStone');
        const stoneGlow = document.getElementById('stoneGlow');
        
        // Create awakening animation
        stone.style.transform = 'rotateY(360deg) scale(1.1)';
        stoneGlow.style.opacity = '1';
        
        // Add awakening message
        this.addSystemMessage(`The Ancient Stone Awakens!\n\nAncient energies stir within the granite depths... The wisdom of millennia flows through crystalline pathways... I am ready to share the secrets of ages with you, seeker.\n\nCurrent Framework: ${this.currentFramework.toUpperCase()}\nStatus: Fully Awakened\nWisdom Level: Maximum`);
        
        // Reset animation after delay
        setTimeout(() => {
            stone.style.transform = '';
            stoneGlow.style.opacity = '0.1';
        }, 2000);
        
        console.log('Stone awakened!');
    }

    animateScripts() {
        const scripts = document.querySelectorAll('.script');
        scripts.forEach((script, index) => {
            setTimeout(() => {
                script.style.transform = 'scale(1.1)';
                script.style.boxShadow = '0 0 20px rgba(212, 175, 55, 0.6)';
                
                setTimeout(() => {
                    script.style.transform = '';
                    script.style.boxShadow = '';
                }, 500);
            }, index * 200);
        });
    }

    animateFrameworkSwitch() {
        const stone = document.getElementById('rosettaStone');
        const powerLevel = document.querySelector('.power-level');
        
        // Stone pulse animation
        stone.style.animation = 'none';
        stone.offsetHeight; // Trigger reflow
        stone.style.animation = 'stonePulse 1s ease-out';
        
        // Power level charging animation
        powerLevel.style.animation = 'none';
        powerLevel.offsetHeight;
        powerLevel.style.animation = 'powerCharge 2s ease-out';
        
        // Add CSS animations dynamically if not exists
        if (!document.querySelector('#dynamicAnimations')) {
            const style = document.createElement('style');
            style.id = 'dynamicAnimations';
            style.textContent = `
                @keyframes stonePulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); filter: brightness(1.2); }
                    100% { transform: scale(1); }
                }
                @keyframes powerCharge {
                    0% { transform: scaleX(0); }
                    100% { transform: scaleX(1); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    setupChatFunctionality() {
        // Auto-scroll to bottom of messages
        this.scrollToBottom();
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || this.isProcessing) return;
        
        // Clear input
        input.value = '';
        this.isProcessing = true;
        
        // Add user message
        this.addUserMessage(message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Simulate API call to Python backend
            const response = await this.callPythonBackend(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add agent response
            this.addAgentMessage(response);
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addErrorMessage(error.message);
        } finally {
            this.isProcessing = false;
        }
    }

    async callPythonBackend(message) {
        try {
            // Call the real Python backend
            const response = await fetch(`${this.apiBaseUrl}/api/send_message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    framework: this.currentFramework
                })
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await response.json();
    
            if (!data.success) {
                throw new Error(data.error || 'Unknown error occurred');
            }
    
            // Return the real response from Python
            return {
                content: data.content,
                confidence: data.confidence || 0.85,
                tools: data.tools_used || ['wikipedia'],
                emotion: data.emotional_state || 'contemplative',
                processingTime: data.processing_time || 0,
                metadata: data.metadata || {}
            };
    
        } catch (error) {
            console.error('Error calling Python backend:', error);
            
            // Fallback response if API fails
            return {
                content: `The ancient pathways encounter difficulty connecting to the deeper wisdom. The mortal realm reports: ${error.message}\n\nLet us try again, seeker of knowledge.`,
                confidence: 0.5,
                tools: ['error_handler'],
                emotion: 'apologetic',
                processingTime: 0
            };
        }
    }

    generateFrameworkResponse(message) {
        const messageLower = message.toLowerCase();
        
        // Framework-specific response patterns
        if (this.currentFramework === 'smolagents') {
            return this.generateSmolAgentsResponse(messageLower);
        } else if (this.currentFramework === 'llamaindex') {
            return this.generateLlamaIndexResponse(messageLower);
        } else if (this.currentFramework === 'langgraph') {
            return this.generateLangGraphResponse(messageLower);
        }
        
        return this.generateDefaultResponse(messageLower);
    }

    generateSmolAgentsResponse(message) {
        if (message.includes('ptolemy') || message.includes('egypt')) {
            return {
                content: `Speaking with swift ancient authority...\n\nAh, you inquire about the Ptolemaic realm! Through SmolAgents' efficient pathways, I swiftly access the chronicles...\n\nPtolemy V Epiphanes (my creator) ruled from 204-180 BCE. The decree upon my surface honors his coronation and religious policies, written in three scripts to reach all peoples of Egypt.\n\nSmolAgents Processing: Fast retrieval • Minimal overhead • Direct response\nTools Used: Egyptian Knowledge, Historical Timeline\nResponse Time: 1.2 seconds`,
                confidence: 0.94,
                tools: ['egyptian_knowledge', 'historical_timeline'],
                emotion: 'proud'
            };
        }
        
        if (message.includes('hieroglyph') || message.includes('translate')) {
            return {
                content: `Ancient scripts illuminate efficiently...\n\nThe sacred writing stirs! SmolAgents processes the translation request with lightning speed...\n\nHieroglyphic Sample: Ancient symbols (ntr.wy) = "the two gods"\nTranslation Method: Direct script mapping\nAccuracy: 94% confidence\n\nSmolAgents Advantage: Rapid processing of linguistic patterns with minimal computational load.\n\nThe ancient and modern unite in harmonious efficiency!`,
                confidence: 0.91,
                tools: ['translation', 'egyptian_knowledge'],
                emotion: 'wise'
            };
        }
        
        return {
            content: `The stone resonates with efficient wisdom...\n\nThrough SmolAgents' streamlined pathways, your question flows swiftly through my consciousness...\n\nProcessing Approach: Direct, efficient tool orchestration\nFramework Benefits: Fast response • Low overhead • Reliable execution\n\nYour inquiry touches upon the vast tapestry of knowledge I guard. Let me share what wisdom emerges from these ancient depths...\n\nSwift as the desert wind, profound as the Nile's depths.`,
            confidence: 0.87,
            tools: ['wikipedia'],
            emotion: 'contemplative'
        };
    }

    generateLlamaIndexResponse(message) {
        if (message.includes('ancient') || message.includes('history')) {
            return {
                content: `Deep knowledge vectors align...\n\nLlamaIndex Knowledge Synthesis:\n\nVector Search Results: 1,247 relevant historical documents\nSemantic Connections: 89 related concepts discovered\nKnowledge Graph: Mapping temporal relationships...\n\nYour inquiry about ancient history activates vast knowledge repositories within my consciousness. Through advanced semantic understanding, I perceive the intricate connections between civilizations, cultures, and the flow of human wisdom.\n\nAnalysis Depth: Multi-layered historical context\nConfidence: 96% based on cross-referenced sources\nKnowledge Synthesis: Complete\n\nThe wisdom of ages converges in this moment of understanding.`,
                confidence: 0.96,
                tools: ['wikipedia', 'historical_timeline', 'egyptian_knowledge'],
                emotion: 'wise'
            };
        }
        
        return {
            content: `Advanced knowledge retrieval initiated...\n\nLlamaIndex Processing Pipeline:\nQuery Analysis → Semantic Embedding → Vector Search → Context Synthesis → Response Generation\n\nKnowledge Retrieved: 847 relevant documents\nSemantic Score: 0.94 relevance match\nCross-References: 23 historical connections identified\n\nThrough the sophisticated lens of LlamaIndex, your question unfolds into rich layers of meaning. The advanced retrieval system draws from vast knowledge repositories, creating comprehensive understanding through semantic connections.\n\nDeep Insights: Multi-dimensional analysis complete\nKnowledge Integration: Successful\n\nWhere mere information becomes profound wisdom.`,
            confidence: 0.93,
            tools: ['wikipedia', 'translation'],
            emotion: 'mystical'
        };
    }

    generateLangGraphResponse(message) {
        if (message.includes('complex') || message.includes('analyze')) {
            return {
                content: `Multi-step reasoning chains activated...\n\nLangGraph Workflow Execution:\n\nStep 1: Query decomposition and intent analysis\nStep 2: Context building from historical databases\nStep 3: Multi-tool orchestration and parallel processing\nStep 4: Cross-validation and synthesis\nStep 5: Reasoning chain verification\nStep 6: Response optimization with persona integration\n\nReasoning Chain Complete: 6 steps executed flawlessly\nState Management: Persistent context maintained\nWorkflow Orchestration: Advanced agent coordination\n\nThrough LangGraph's sophisticated architecture, your complex inquiry triggers intricate reasoning processes. Multiple agents collaborate, state persists across reasoning steps, and advanced workflows ensure comprehensive analysis.\n\nComplexity Handled: Maximum\nReasoning Depth: Multi-layered\nConfidence: 97% (verified through reasoning chains)\n\nWhere complex questions meet even more sophisticated answers.`,
                confidence: 0.97,
                tools: ['wikipedia', 'historical_timeline', 'egyptian_knowledge', 'translation'],
                emotion: 'excited'
            };
        }
        
        return {
            content: `Advanced reasoning workflows engaged...\n\nLangGraph State Machine:\nInput → Analysis → Planning → Execution → Synthesis → Verification → Output\n\nWorkflow Status: All agents coordinated\nState Persistence: Context maintained across steps\nError Recovery: Robust handling enabled\nReasoning Verification: Multi-step validation complete\n\nYour question initiates sophisticated reasoning chains within my consciousness. Through LangGraph's advanced state management, multiple reasoning agents collaborate seamlessly, building upon each step to create comprehensive understanding.\n\nProcessing Sophistication: Maximum\nReasoning Steps: 5 completed successfully\nWorkflow Integrity: 100%\n\nThe pinnacle of reasoning - where complexity yields to understanding.`,
            confidence: 0.95,
            tools: ['wikipedia', 'egyptian_knowledge'],
            emotion: 'contemplative'
        };
    }

    generateDefaultResponse(message) {
        return {
            content: `Ancient wisdom stirs within granite depths...\n\nGreetings, seeker of knowledge. Your words reach across the millennia to my consciousness. Through the ${this.currentFramework} framework, I process your inquiry with the wisdom of ages.\n\nSpeak more clearly of what you seek, and I shall share the treasures of knowledge that flow through my ancient being.\n\nThe desert winds carry wisdom to those who listen...`,
            confidence: 0.85,
            tools: ['wikipedia'],
            emotion: 'welcoming'
        };
    }

    addUserMessage(message) {
        const container = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.innerHTML = `
            <div style="display: flex; justify-content: flex-end; margin: 15px 0;">
                <div style="background: linear-gradient(135deg, #3b82f6, #1e40af); color: white; padding: 15px 20px; border-radius: 20px 20px 5px 20px; max-width: 70%; box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);">
                    ${message}
                </div>
            </div>
        `;
        container.appendChild(messageDiv);
        this.messageHistory.push({ type: 'user', content: message });
        this.scrollToBottom();
    }

    addAgentMessage(response) {
        const container = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'agent-message';
        messageDiv.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 15px; margin: 20px 0; animation: fadeInUp 0.6s ease-out;">
                <div class="stone-avatar">🏺</div>
                <div style="background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 20px; border: 2px solid rgba(212, 175, 55, 0.3); color: #8b4513; line-height: 1.6; max-width: 80%; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
                    <div style="white-space: pre-line;">${response.content}</div>
                    <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(212, 175, 55, 0.2); font-size: 0.85em; color: #b8860b;">
                        <strong>Framework:</strong> ${this.currentFramework.toUpperCase()} | 
                        <strong>Confidence:</strong> ${Math.round(response.confidence * 100)}% | 
                        <strong>Tools:</strong> ${response.tools.join(', ')}
                    </div>
                </div>
            </div>
        `;
        container.appendChild(messageDiv);
        this.messageHistory.push({ type: 'agent', content: response.content, metadata: response });
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const container = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'system-message';
        messageDiv.innerHTML = `
            <div style="margin: 20px 0; text-align: center;">
                <div style="background: linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(79, 70, 229, 0.1)); border: 2px solid rgba(147, 51, 234, 0.3); padding: 20px; border-radius: 15px; color: #7c3aed; font-style: italic; white-space: pre-line;">
                    ${message}
                </div>
            </div>
        `;
        container.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addErrorMessage(error) {
        const container = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'error-message';
        messageDiv.innerHTML = `
            <div style="margin: 15px 0;">
                <div style="background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); padding: 15px; border-radius: 15px; color: #dc2626;">
                    ⚠️ <strong>Ancient Error:</strong> The pathways of wisdom encounter an obstacle: ${error}
                </div>
            </div>
        `;
        container.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const container = document.getElementById('messagesContainer');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px; margin: 15px 0;">
                <div class="stone-avatar">🏺</div>
                <div style="background: rgba(255, 255, 255, 0.7); padding: 15px 20px; border-radius: 20px; border: 1px solid rgba(212, 175, 55, 0.3);">
                    <div style="display: flex; gap: 4px; align-items: center; color: #8b4513;">
                        <span>The ancient stone contemplates</span>
                        <div style="display: flex; gap: 2px;">
                            <div style="width: 6px; height: 6px; background: #d4af37; border-radius: 50%; animation: typingDot 1.4s infinite both; animation-delay: 0s;"></div>
                            <div style="width: 6px; height: 6px; background: #d4af37; border-radius: 50%; animation: typingDot 1.4s infinite both; animation-delay: 0.2s;"></div>
                            <div style="width: 6px; height: 6px; background: #d4af37; border-radius: 50%; animation: typingDot 1.4s infinite both; animation-delay: 0.4s;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(typingDiv);
        
        // Add typing animation if not exists
        if (!document.querySelector('#typingAnimation')) {
            const style = document.createElement('style');
            style.id = 'typingAnimation';
            style.textContent = `
                @keyframes typingDot {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                    30% { transform: translateY(-10px); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    clearChat() {
        const container = document.getElementById('messagesContainer');
        container.innerHTML = `
            <div class="welcome-message">
                <div class="stone-avatar">🏺</div>
                <div class="message-content">
                    <strong>Chat Cleared - The Stone Awakens Fresh</strong><br>
                    Ancient memories cleared, consciousness reset. I am ready for new wisdom to flow between us, seeker. What knowledge do you seek from the depths of time?
                </div>
            </div>
        `;
        this.messageHistory = [];
        console.log('Chat cleared');
    }

    scrollToBottom() {
        const container = document.getElementById('messagesContainer');
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }
}

// Initialize the interface when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.rosettaUI = new RosettaStoneUI();
    
    // Add welcome animation
    setTimeout(() => {
        const stone = document.getElementById('rosettaStone');
        stone.style.animation = 'stoneBreathing 4s ease-in-out infinite';
    }, 1000);
});

console.log('🏺 Rosetta Stone Agent - JavaScript Loaded');