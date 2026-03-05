# Page snapshot

```yaml
- generic [ref=e4]:
  - generic [ref=e5]:
    - img "SurvAI"
    - paragraph [ref=e6]: Agency Login
  - generic [ref=e7]:
    - generic [ref=e8]:
      - generic [ref=e9]:
        - text: Username
        - generic [ref=e10]: "*"
      - generic [ref=e11]:
        - textbox "Username" [active] [ref=e12]
        - group:
          - generic: Username *
    - generic [ref=e13]:
      - generic:
        - text: Password
        - generic: "*"
      - generic [ref=e14]:
        - textbox "Password" [ref=e15]
        - group:
          - generic: Password *
    - button "Sign In" [ref=e16] [cursor=pointer]
  - paragraph [ref=e17]: Contact your administrator for access credentials
```