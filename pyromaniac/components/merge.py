{
    'ignition.config.merge': [
        { 'inline': render(conf) } for conf in args if conf is not None
    ]
}
