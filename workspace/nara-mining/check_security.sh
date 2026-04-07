#!/bin/bash
# Security check untuk NARA wallet folders

echo "🔒 NARA Wallet Security Check"
echo "=============================="
echo ""

WALLET_DIR="$HOME/.nara-wallets"
MNEMONIC_DIR="$HOME/.nara-mnemonics"

# Check wallet directory
if [ -d "$WALLET_DIR" ]; then
    echo "📁 Wallet directory: $WALLET_DIR"
    
    # Check permissions
    PERM=$(stat -c "%a" "$WALLET_DIR")
    if [ "$PERM" = "700" ]; then
        echo "   ✅ Permission: 700 (correct)"
    else
        echo "   ⚠️  Permission: $PERM (should be 700)"
        echo "   🔧 Fixing..."
        chmod 700 "$WALLET_DIR"
    fi
    
    # Check .gitignore
    if [ -f "$WALLET_DIR/.gitignore" ]; then
        echo "   ✅ .gitignore exists"
    else
        echo "   ⚠️  .gitignore missing"
    fi
    
    # Count wallets
    COUNT=$(ls -1 "$WALLET_DIR"/*.json 2>/dev/null | wc -l)
    echo "   📊 Wallets: $COUNT"
else
    echo "❌ Wallet directory not found"
fi

echo ""

# Check mnemonic directory
if [ -d "$MNEMONIC_DIR" ]; then
    echo "📁 Mnemonic directory: $MNEMONIC_DIR"
    
    PERM=$(stat -c "%a" "$MNEMONIC_DIR")
    if [ "$PERM" = "700" ]; then
        echo "   ✅ Permission: 700 (correct)"
    else
        echo "   ⚠️  Permission: $PERM (should be 700)"
        chmod 700 "$MNEMONIC_DIR"
    fi
    
    # Count mnemonic files
    MCOUNT=$(ls -1 "$MNEMONIC_DIR"/*-mnemonic.txt 2>/dev/null | wc -l)
    echo "   📝 Mnemonic files: $MCOUNT"
else
    echo "⚠️  Mnemonic directory not found"
fi

echo ""
echo "=============================="
echo "⚠️  REMEMBER:"
echo "   - Backup mnemonics OFFLINE (paper)"
echo "   - NEVER upload wallet files to GitHub"
echo "   - Store backups in secure location"
echo "=============================="
